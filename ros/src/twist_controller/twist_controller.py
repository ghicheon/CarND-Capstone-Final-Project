from pid import PID
from lowpass import LowPassFilter
from yaw_controller import YawController
import rospy


GAS_DENSITY = 2.858
ONE_MPH= 0.44704

#to drive slowly when start. if not, sometimes the car miss the traffic light.
BASE_VEL=0.2
throttle_for_slowstart = [BASE_VEL ,BASE_VEL*2 ,BASE_VEL*3 ,BASE_VEL*4 ,BASE_VEL*5,BASE_VEL*6,BASE_VEL*7]


class Controller(object):
    def __init__(self, vehicle_mass,fuel_capacity, brake_deadband, decel_limit, 
                 accel_limit, wheel_radius, wheel_base, steer_ratio, max_lat_accel, max_steer_angle):
        
        #FOPDT(first order plus dead-time model is used.
        #Tuning is done using IMC(Internal Model Control) 
        kp=0.5      
        ki=kp/8.0

        kd = 0.0
        mn = 0. #Minimum throttle value
        mx = 0.5 #Maximum throttle value
        
        self.steering_controller = PID(kp, ki, kd, mn, mx)
        self.throttle_controller = PID(kp, ki, kd, mn, mx)
        self.yaw_controller = YawController(wheel_base, steer_ratio, 0.1, max_lat_accel, max_steer_angle)
        
        tau = 0.5 # 1/(2pi*tau) = cutoff frequency
        ts = .02 # Sample time
        self.vel_lpf = LowPassFilter(tau, ts)
        
        self.vehicle_mass = vehicle_mass
        self.fuel_capacity = fuel_capacity
        self.brake_deadband = brake_deadband
        self.decel_limit = decel_limit
        self.accel_limit = accel_limit
        self.wheel_radius = wheel_radius
        self.last_time = rospy.get_time()

    def control(self, current_vel, curr_ang_vel, linear_vel, angular_vel, dbw_enabled):
        
        if not dbw_enabled:
            self.throttle_controller.reset()
            return 0., 0., 0.
        
        current_vel = self.vel_lpf.filt(current_vel)
        vel_error = linear_vel - current_vel
        self.last_vel = current_vel
        
        steering_estimate = self.yaw_controller.get_steering(linear_vel, angular_vel, current_vel)
        
        current_time = rospy.get_time()
        sample_time = current_time - self.last_time
        self.last_time = current_time
        
        throttle = self.throttle_controller.step(vel_error, sample_time)
        brake = 0
        
        ang_vel_error = angular_vel - curr_ang_vel
        steering_correction = self.steering_controller.step(ang_vel_error, sample_time)
        steering = steering_estimate + steering_correction
        
        if linear_vel == 0 and current_vel < 0.1:
            throttle = 0.0
            brake = 450
            
        elif throttle < 0.1 and vel_error < 0:
            throttle = 0.0
            decel = max(vel_error, self.decel_limit)
            brake = abs(decel) * (self.vehicle_mass + GAS_DENSITY * self.fuel_capacity) * self.wheel_radius

        # current_vel is m/s. therefore 5m/s is around 20 km/h
        vel_idx = int(current_vel)
        if vel_idx < 7 :    
            limit  = throttle_for_slowstart[vel_idx]
            throttle = limit if current_vel > limit else current_vel

        return throttle, brake, steering
