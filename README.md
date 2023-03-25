# **AK Streaming Application**

Part 1: Installation & Setup

Part 2: Application Structure & Functionality

* Backend
* Frontend
* Streaming Process

Part 3: Project Screenshots

---

## Installation & Setup:

* Clone the repository with **git clone https://github.com/artulidis/webstream-final.git**
    
* Create an .env file in the root directory of the project and add the following credentials:

    * **POSTGRES_DB**: the name of the PostgreSQL database.

    * **POSTGRES_USER**: the PostgreSQL username.

    * **POSTGRES_PASSWORD**: the PostgreSQL password.

    * **SECRET_KEY**: the secret key for Django sessions and cookies.

* This application is runs best on a Linux machine.

* To use the application on a Linux machine, install a **video0** video driver by running the following command in the system's root directory:<br /> **mknod /dev/video0 c 81 0**.

---

## Application Structure & Functionality

The following diagram depicts the general structure of the application's design and how browser requests are handled. 

<br />

![Application Structure Diagram](/assets/application-diagram.png)

<br />

The website is hosted inside a Docker container and uses Docker Compose to build all the services with proper configurations and in the correct order. The app consists of six services:

1.  Django: The backend server is responsible for handling requests from the frontend, processing data, and interacting with the database.
    
2.  React: The frontend server is responsible for rendering the user interface and handling user interactions.

3.  Postgres: The database server stores and retrieves data from the database.

4.  Redis: The in-memory database server is used as a message broker to send messages across channel layers.

5.  Celery: The distributed task queue is used to process asynchronous tasks, such as starting live streams.

6.  Nginx: The web server is used as a reverse proxy to handle incoming requests and route them to the appropriate service. The Nginx server uses the nginx-tiangolo image for RTMP compatibility.

When the website is first loaded, a request is sent to Nginx to retrieve all necessary files needed to load the site, including:

 * React build files: These files are used to load the frontend user interface.

* Static files: These files include user-uploaded information such as user profile pictures and stream thumbnails.

* Daphne ASGI server: This server is used to handle either HTTP requests to the API or WebSocket connections to enable live chat functionality. The live stream also starts through an HTTP request, which triggers a Celery task that starts FFmpeg.

---

## Backend:

The backend of the application is responsible mainly for two functions:

* Handling the request/response cycle
* Managing data

### Request / Response Cycle

Daphne ASGI Server is used in the application as a gateway interface between Nginx and the Django application. When a request is received, it is passed to the Protocol Type Router, which determines whether the request is HTTP or a web socket connection.

#### HTTP Requests:

The application uses HTTP requests to either communicate with the API, or to start the streaming process.

* Django REST Framework is used in combination with serializers to present data stored in the Postgres database on a specific URL in JSON format. The frontend of the application uses this API to communicate with the database.

* The **start** view, which is located in the **rtmp** app, receives and decodes POST requests from the frontend and passes the necessary information to celery. The POST request contains an Ffmpeg command with the following optional settings:

    * Stream duration
    * Stream resolution
    * Frame rate
    * Bit rate

    <br />

    ```
    def start(request):
        if request.method == "POST":
            body = json.loads(request.body.decode('utf-8')) 
            ffmpeg_command = body["ffmpegCommand"]
            ip_addr = request.META.get('REMOTE_ADDR')
            push_stream.delay(ip_addr, ffmpeg_command)
            data = {
                "ip": ip_addr
            }
            return JsonResponse(data)
    ```

    <br  />

    The application's frontend composes the Ffmpeg command with an additional stream key variable so that each stream has a unique identifier. The start view  grabs the application's IP address so that it can adapt to the varying IP addresses assigned to the Nginx Docker container, which later uses it to successfully configure a stream. The purpose of the start view is to pass the Ffmpeg command with the application's IP address to a Celery task called **push_stream** that initiates the stream.

    ```
    def push_stream(ip_addr, ffmpeg_command):
        ffmpeg_command = ffmpeg_command.replace("127.0.0.1", ip_addr)
        os.system(ffmpeg_command)
    ```
    
    ```
    ffmpeg -f video4linux2 -i /dev/video0 -t 5 -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -s 1200x720 -r 30 -b:v 1500k -maxrate 7000k -c:a aac -b:a 128k -ac 2 -ar 44100 -f flv rtmp://127.0.0.1:1935/live/0006
    ```

<br />

#### Web Socket Connections:

The application uses Django Channels to handle web socket events. When the Protocol Type Router receives a web socket connection request, it forwards the request to a consumer which then accepts and processes connections to make sure the users are assigned a proper group. In this case, the channel's group is the stream that a user selected. When a message has been sent from the frontend, the consumer directs the message to Redis - a message broker that is used to broadcast messages through the channel layer to all recipients of a group. From there, the message is stored in the Postgres database and is sent back to the frontend, allowing users to view messages both in real-time and after the stream has been recorded.

```
async def websocket_receive(self, event):
        front_text = event.get('text', None)
        if front_text is not None:
            message_data = json.loads(front_text)
            message = message_data.get('body')

            new_message = await self.create_message(message)

            response = {
                'user': new_message.user.username,
                'body': new_message.body,
                'video': new_message.video.id,
                'created': str(new_message.created)
            }

            await self.channel_layer.group_send(
                self.stream_chat,
                {
                    'type': 'message_event',
                    'text': json.dumps(response)
                }
            )
```

<br />

### Managing Data

Postgres is used to store the application's data with Django's Models providing a layer of abstraction to allow the data to be manipulated. The tables in the database include the following information:

* User Information
* User Following/Follower Relationships
* Stream Information
* Stream Topics
* Stream Comments

The User Manager has been overwritten to define necessary user information and enable compatibility with JWT Authentication.

```
class MyUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(
            username=username
        )
        user.is_active=True
        user.is_superuser=False
        user.is_staff=False
        user.set_password(password)
        user.save(using=self._db)
        return user
```

---

## Frontend:

React.js is the frontend framework used in this project and is responsible for loading a smooth user interface and sending user requests and events to the backend.

<br />

* Some of the key features of the application's User Interface include:

    * Smooth content updates that are made possible with React's state management system.

    * Stream filtering through either a search bar or topic tabs.

    * Customized Video.js stream viewer that accurately matches application's theme.

    * Configuration form for desired stream settings and output.

<br />

* Axios is the main tool for sending HTTP requests due to its configurability and ease of use. It has been configured with interceptors that refresh users' access tokens everytime information-sensitive requests are sent to the backend. JWT Authentication, made possible with Axios interceptors, enables users to log into the application once, without the need for verification every time their session is expired. The access token is stored in a browser's local storage.

    ```
    interceptorInstance.interceptors.request.use(async req => {

        const user = jwt_decode(authTokens.access)
        const isExpired = dayjs.unix(user.exp).diff(dayjs()) < 1;

        if(!isExpired) return req

        const response = await axios.post(`${baseURL}api/token/refresh/`, {
            refresh: authTokens.refresh
        });

        localStorage.setItem('authTokens', JSON.stringify(response.data))
        
        setAuthTokens(response.data)
        setUser(jwt_decode(response.data.access))
        
        req.headers.Authorization = `Bearer ${response.data.access}`
        return req
    })
        
        return interceptorInstance
    }
    ```

    HTTP requests are also sent to the backend to retrieve, update, and delete data from the database.

---

## The Streaming Process:

In the beginning phases of development, the application employed a third-party plugin called Agora.io, which allowed a plug-and-play method for streaming video with javascript. As development continued, the inner workings of the streaming process itself became a focus of the project. Currently, the Nginx RTMP module is used together with Ffmpeg to produce a stream that is received by Video.js on the frontend.

When a user decides they want to start a stream, a form is displayed with a preview of their camera; inputs for generic information like stream name, description, and topics; along with inputs for more advanced settings that are used to compose the Ffmpeg command.

As mentioned previously in this README, the frontend sends a request to the start view of the backend, triggering the stream process upon user input. Celery starts the **push_stream** task - a function that runs the Ffmpeg command on the os asynchronously, preventing the stream from blocking the application. 

Ffmpeg pushes a video stream to Nginx on **port 1935** with settings specified by the user. There are two important configurations required for the stream to be pushed and served to the browser:

```
rtmp {
	server {
		listen 1935;
		chunk_size 4000;
		allow publish all;

		application live {

			live on;

			record all;
			record_path /var/www/stream/hls;
			exec_record_done ffmpeg -y -i $path -acodec libmp3lame -ar 44100 -ac 1 -vcodec libx264 var/www/stream/rec/$basename.mp4;

			hls on;
			hls_path /var/www/stream/hls;
			hls_fragment 3;
			hls_playlist_length 60;
			
			dash on;
			dash_path /var/www/stream/dash;

		}
	}
}
```

```
server {
    listen 8080;

    location / {
        add_header Access-Control-Allow-Origin *;
        root /var/www/stream;
    }
}

types {
    application/dash+xml mpd;
}
```

The first configuration file sets up an RTMP server on **port 1935** and defines an application called **live**. The **live** application is responsible for handling incoming video streams, recording them, and serving them via HLS and DASH.

To convert the incoming RTMP stream to HLS and DASH, the **live** application is configured with the **hls on** and **dash on** directives. The "hls_path" and **dash_path** directives define the location where the HLS and DASH files will be saved.

The **record_path** directive specifies the location where the incoming video stream will be recorded. The **exec_record_done** directive specifies a command to run after the recording is complete. In this case, the command runs ffmpeg to convert the recorded video to an **mp4** file.

To serve the HLS files to the browser in **m3u8** format, the **hls_fragment** and **hls_playlist_length** directives define the duration of each video segment and the duration of the HLS playlist respectively. The resulting HLS files are served to the browser via HTTP on **port 8080**, as defined in the second configuration file.

---

## Project Screenshots:

<br />

![AK Streaming Discover](/assets/akstream-discover.png)

![AK Streaming Configure](/assets/akstream-configure.png)

![AK Streaming Profile](/assets/akstream-profile.png)

![AK Streaming Watch](/assets/akstream-watch.png)

<br />
