# Late Start But Best Team

## team organization

|  Name                                   |  Email Address                    |
|:---------------------------------------:|:---------------------------------:|
| Ghicheon Lee (**Team Leader**)          |   gebmania@gmail.com              |
| Elle Li                                 |  zheyuanli99@gmail.com            |
| Haiqi Bian                              |   bingo.hiqi@gmail.com            |
| David Göndör                            |   gondordavid@gmail.com           |
| Venkat Sai Raxit Karramreddy            |   vkarramr@mtu.edu                |

## Requirements

* Launch correctly using the launch files provided in the capstone repo. Please note that we will not be able to accommodate special launch instructions or run additional scripts from your submission to download files. The launch/styx.launch and launch/site.launch files will be used to test code in the simulator and on the vehicle respectively. The submission size limit for this project has been increased to 2GB.
* Smoothly follow waypoints in the simulator.
* Respect the target top speed set for the waypoints' twist.twist.linear.x in waypoint_loader.py. Be sure to check that this is working by testing with different values for kph velocity parameter in /ros/src/waypoint_loader/launch/waypoint_loader.launch. If your vehicle adheres to the kph target top speed set here, then you have satisfied this requirement.
* Stop at traffic lights when needed.
* Stop and restart PID controllers depending on the state of /vehicle/dbw_enabled.
* Publish throttle, steering, and brake commands at 50hz.

## Contributions

### Traffic light detector

The detector is used to:

* find the closest waypoint to the ego vehicle
* find the closest traffic light
* call the traffic light classifier
* if the traffic light is `RED`, publish the waypoint to `/traffic_waypoint` topic

### Traffic light classifier (Haiqi Bian)

The classifier is used to classify the detected traffic light to 4 categories: `RED`, `GREEN`, `YELLOW` and `OFF`.
Training the classification by using SSD Inception V2 Coco. There are 2 training results, batch size 8 and batch size 24. The "batch size 24" was trained at AWS EC2 Instance and the "batch size 8" was trained on local PC due to the GPU memory limitation.
The `.pd` files are located at following path:

* for udacity-simulator (./ros/src/tl_detector/light_classification/model/sim):
  * ./8_batch/frozen_inference_graph.pb
  * ./24_batch/frozen_inference_graph.pb (default)
* for udacity parking lot (./ros/src/tl_detector/light_classification/model/real):
  * ./8_batch/frozen_inference_graph.pb
  * ./24_batch/frozen_inference_graph.pb (default)

### DBW node (David Göndör)

Made the dbw node to subcribe to the /twist_cmd and use various controllers to provide appropriate throttle, brake, and steering commands.  

### Waypoint updater (Venkat)

### PID controller tunning (Ghicheon Lee)

Conditional integral was applied to PID controller.         
FOPDT(first order plus dead-time model) parameters were found. IMC(Internal Model Control) tunning was used.               
MPC model was considered (https://github.com/ghicheon/code_snippets) but not used because it's too slow in python.     

I modified code like following in order to measure FOPDT parameters.             

* There is no speed limit       

```bash
waypoint_loader.launch           
      <param name="velocity" value="100" />          
```

* throttle is always 30%.             
  
```bash
twist_controller.py       
   def control(self, current_vel, curr_ang_vel, linear_vel, angular_vel, dbw_enabled):     
        ...
        throttle = 0.3      
        brake = 0        
        return throttle, brake, steering     
```

#### FOPDT parameters       
* K_p = dy/du = 16/30       
dy: the maximum speed (m/s) with du   => 16 m/s       
du: the throttle %                               => 30%       
     
The maximum speed is 35.84 miles/hour. it's 57.67 km/hour. it's also 16 meters/second       
The throttle is 30%         
             
* theta_p = 0   
How long does it take the car to response. It must be close to 0 in modern cars.        
   
* tau_p = 10                 
How long does it take the car to reach the 63% of the maximum speed.            
      
35.84 * 0.63 = 22.57 miles/hour        
     
I measured the time to reach 22.57 MPH.  it was 10 seconds.        

#### IMC Moderate Tunning  
P: K_c   
I: K_c/tau_I    
D: K_c * tau_D   

We're going to use PI parameters.     
K_c = 1/K_p        

tau_c = 1.0 * tau_p     
tau_I = tau_p   
K_c/tau_I = K_c / tau_p     

In conclusion,  P parameter is 1/K_p = 1/(16/30) = 30/16    and I parameter is K_c/tau_p = (30/16)/10.
After getting IMC tunning values, I tried to find more accurate values manually.   
            
        
#### Conditional integral
Integral term is disable when error is the same sign with PID output and it's saturated.     
```python
   def step(self, error, sample_time):
        integral = self.int_val + error * sample_time;
        derivative = (error - self.last_error) / sample_time;

        if self.integral_on == True:
            val = self.kp * error + self.ki * integral + self.kd * derivative;
        else:
            val = self.kp * error + self.kd * derivative;
            
        ...

        same_sign = (error > 0 and val > 0 ) or (error < 0 and val < 0 )

        if saturated and same_sign: 
                self.integral_on = False
        else:
                self.integral_on = True  #turn on again!

        return val
```
#### References
FOPDT & IMC reference                
http://apmonitor.com/pdc/index.php/Main/FirstOrderSystems 
https://www.youtube.com/watch?v=k46nCvOBllA&t=340s

conditional integral reference              
https://www.youtube.com/watch?v=NVLXCwc8HzM&list=PLn8PRpmsu08pQBgjxYFXSsODEF3Jqmm-y&index=2           

#### Epilogue          
I just wanna say...           
"There is a difference between knowing the path and walking the path." – Morpheus(The Matrix 1999)         
        

-------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------


This is the project repo for the final project of the Udacity Self-Driving Car Nanodegree: Programming a Real Self-Driving Car. For more information about the project, see the project introduction [here](https://classroom.udacity.com/nanodegrees/nd013/parts/6047fe34-d93c-4f50-8336-b70ef10cb4b2/modules/e1a23b06-329a-4684-a717-ad476f0d8dff/lessons/462c933d-9f24-42d3-8bdc-a08a5fc866e4/concepts/5ab4b122-83e6-436d-850f-9f4d26627fd9).

Please use **one** of the two installation options, either native **or** docker installation.

## Native Installation

* Be sure that your workstation is running Ubuntu 16.04 Xenial Xerus or Ubuntu 14.04 Trusty Tahir. [Ubuntu downloads can be found here](https://www.ubuntu.com/download/desktop).
* If using a Virtual Machine to install Ubuntu, use the following configuration as minimum:
  * 2 CPU
  * 2 GB system memory
  * 25 GB of free hard drive space

  The Udacity provided virtual machine has ROS and Dataspeed DBW already installed, so you can skip the next two steps if you are using this.

* Follow these instructions to install ROS
  * [ROS Kinetic](http://wiki.ros.org/kinetic/Installation/Ubuntu) if you have Ubuntu 16.04.
  * [ROS Indigo](http://wiki.ros.org/indigo/Installation/Ubuntu) if you have Ubuntu 14.04.
* [Dataspeed DBW](https://bitbucket.org/DataspeedInc/dbw_mkz_ros)
  * Use this option to install the SDK on a workstation that already has ROS installed: [One Line SDK Install (binary)](https://bitbucket.org/DataspeedInc/dbw_mkz_ros/src/81e63fcc335d7b64139d7482017d6a97b405e250/ROS_SETUP.md?fileviewer=file-view-default)
* Download the [Udacity Simulator](https://github.com/udacity/CarND-Capstone/releases).

## Docker Installation
[Install Docker](https://docs.docker.com/engine/installation/)

Build the docker container
```bash
docker build . -t capstone
```

Run the docker file
```bash
docker run -p 4567:4567 -v $PWD:/capstone -v /tmp/log:/root/.ros/ --rm -it capstone
```

## Port Forwarding
To set up port forwarding, please refer to the "uWebSocketIO Starter Guide" found in the classroom (see Extended Kalman Filter Project lesson).

## Usage

1. Clone the project repository
```bash
git clone https://github.com/udacity/CarND-Capstone.git
```

2. Install python dependencies
```bash
cd CarND-Capstone
pip install -r requirements.txt
```
3. Make and run styx
```bash
cd ros
catkin_make
source devel/setup.sh
roslaunch launch/styx.launch
```
4. Run the simulator

## Real world testing
1. Download [training bag](https://s3-us-west-1.amazonaws.com/udacity-selfdrivingcar/traffic_light_bag_file.zip) that was recorded on the Udacity self-driving car.
2. Unzip the file
```bash
unzip traffic_light_bag_file.zip
```
3. Play the bag file
```bash
rosbag play -l traffic_light_bag_file/traffic_light_training.bag
```
4. Launch your project in site mode
```bash
cd CarND-Capstone/ros
roslaunch launch/site.launch
```
5. Confirm that traffic light detection works on real life images

## Other library/driver information
Outside of `requirements.txt`, here is information on other driver/library versions used in the simulator and Carla:

Specific to these libraries, the simulator grader and Carla use the following:

|        | Simulator | Carla  |
| :-----------: |:-------------:| :-----:|
| Nvidia driver | 384.130 | 384.130 |
| CUDA | 8.0.61 | 8.0.61 |
| cuDNN | 6.0.21 | 6.0.21 |
| TensorRT | N/A | N/A |
| OpenCV | 3.2.0-dev | 2.4.8 |
| OpenMP | N/A | N/A |

We are working on a fix to line up the OpenCV versions between the two.
