from math import atan

class YawController(object):
	def __init__(self, wheel_base, steer_ratio, min_speed, max_lat_accel, max_steer_angle):
		self.wheel_base = wheel_base
		self.steer_ratio = steer_ratio
		self.min_speed = min_speed
		self.max_lat_accel = max_lat_accel

		self.min_angle = -max_steer_angle
		self.max_angle = max_steer_angle
		self.k_damping = -0.8
		self.accumulated_error = -0.06
		self.k_integral = 0.0
		self.last_velocity = 0.0

	def get_angle(self, radius):
		angle = atan(self.wheel_base / radius) * self.steer_ratio
		return max(self.min_angle, min(self.max_angle, angle))

	def get_steering(self, linear_velocity, angular_velocity, current_velocity):
		angular_velocity = current_velocity * angular_velocity / linear_velocity if abs(linear_velocity) > 0. else 0.
		if self.last_velocity ==0 :
			delta_vel = 0.0
			accumulated_error = 0.0


		if abs(current_velocity) > 0.1:
			max_yaw_rate = abs(self.max_lat_accel / current_velocity);
			delta_vel = angular_velocity - self.last_velocity
			self.accumulated_error += angular_velocity
			angular_velocity = max(-max_yaw_rate, min(max_yaw_rate, angular_velocity+ self.k_damping*delta_vel + self.k_integral*self.accumulated_error))
			print('angular velocity is:', angular_velocity)
		return self.get_angle(max(current_velocity, self.min_speed) / angular_velocity) if abs(angular_velocity) > 0. else 0.0


if __name__ == "__main__":

	yawcontroller = YawController(2,0.1,0.01,1.0,2.)

    # catkin_make && source devel/setup.sh && roslaunch launch/styx.launch
