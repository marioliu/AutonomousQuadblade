# !/usr/bin/python
'''
Adapted from https://github.com/ivmech/ivPID
'''
import time

class PID:
    """
    PID Controller
    """

    def __init__(self, P=0.5, I=0.0, D=0.0):
        '''
        Initializes the PID controller.

        Parameters
        ----------
            P: Proportional gain
            I: Integral gain
            D: Derivative gain
        '''
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.sample_time = 0.00
        self.current_time = time.time()
        self.last_time = self.current_time

        self.clear()

    def clear(self):
        """
        Clears PID computations and coefficients.
        """
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.int_error = 0.0
        self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value):
        """
        Calculates PID value for given reference feedback.
        
        Math
        ----
            u(t) = K_p e(t) + K_i integral{0}^{t} (e(t)dt) + K_d {de}/{dt}

        Returns the controller output for the given feedback.
        """
        error = self.SetPoint - feedback_value

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if (self.ITerm < -self.windup_guard):
                self.ITerm = -self.windup_guard
            elif (self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error

            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)

        return self.output

    def setKp(self, proportional_gain):
        """
        Determines how aggressively the PID reacts to the current error with setting Proportional Gain.
        """
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """
        Determines how aggressively the PID reacts to the current error with setting Integral Gain.
        """
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """
        Determines how aggressively the PID reacts to the current error with setting Derivative Gain.
        """
        self.Kd = derivative_gain

    def setWindup(self, windup):
        """
        Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where a large change in setpoint occurs (say a positive change) and the integral terms accumulates a significant error during the rise (windup),
        thus overshooting and continuing to increase as this accumulated
        error is unwound (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        """
        PID that should be updated at a regular interval.
        Based on a pre-determined sample time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time

    def setSetPoint(self, s):
        '''
        Sets the value that the controller will track.
        '''
        self.SetPoint = s

def main():
    '''
    Unit testing.
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.interpolate import BSpline, make_interp_spline

    P = 1.2
    I = 1
    D = 0.00
    L = 100

    pid = PID(P, I, D)

    pid.setSetPoint(0.0)
    pid.setSampleTime(0.01)

    feedback = 0

    feedback_list = []
    time_list = []
    # set values for controller to track
    setpoint_list = [0] * (L/5) + [1] * (L/5) + [2] * (L/5) + [-1] * (L/5) + [-1] * (L/5)

    for i in range(1, L):
        output = pid.update(feedback)

        sp = setpoint_list[i]
        pid.setSetPoint(sp)
        
        feedback += (output - (1/i))
        
        time.sleep(0.02)

        feedback_list.append(feedback)
        time_list.append(i)

    time_sm = np.array(time_list)
    time_smooth = np.linspace(time_sm.min(), time_sm.max(), 300)

    # feedback_smooth = spline(time_list, feedback_list, time_smooth)
    # Using make_interp_spline to create BSpline
    helper_x3 = make_interp_spline(time_list, feedback_list)
    feedback_smooth = helper_x3(time_smooth)

    plt.plot(time_list, setpoint_list[1:], LineWidth = 1.5, label='Value to Track')
    plt.plot(time_smooth, feedback_smooth, label='Controller Response')
    plt.xlim((0, L))
    plt.ylim((min(setpoint_list)-1, max(setpoint_list)+1))
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('PID Controller')
    plt.legend()

    plt.grid()
    plt.show()

if __name__ == '__main__':
    main()