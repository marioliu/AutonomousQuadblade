%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Authors: Mario Liu and Nadir Noordin
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

clear all;
close all;

% test transformation matrices for accuracy
syms phi theta psi dphi dtheta dpsi

% transform from inertial to body
R_I_B = [cos(psi)*cos(theta) sin(psi)*cos(theta) -sin(theta);
    cos(psi)*sin(theta)*sin(phi)-cos(phi)*sin(psi) ...
    sin(psi)*sin(theta)*sin(phi)+cos(phi)*cos(psi) cos(theta)*sin(phi);
    cos(phi)*sin(theta)*cos(psi)+sin(phi)*sin(psi) ...
    sin(psi)*sin(theta)*cos(phi)-sin(phi)*cos(psi) cos(theta)*cos(phi)];

% transform from body to inertial
R_B_I = simplify(R_I_B^-1);

R_psi = [cos(psi) sin(psi) 0;
    -sin(psi) cos(psi) 0;
    0 0 1];

R_theta = [cos(theta) 0 -sin(theta);
    0 1 0;
    sin(theta) 0 cos(theta)];

R_phi = [1 0 0;
    0 cos(phi) sin(phi);
    0 -sin(phi) cos(phi)];

R_final = R_phi*R_theta*R_psi; % should equal R_I_B

w = R_phi*R_theta*[0; 0; dpsi] + R_phi*[0; dtheta; 0] + [dphi; 0; 0];
% transforming angular velocities
T_I_B = [1 0 -sin(theta);
    0 cos(phi) sin(phi)*cos(theta);
    0 -sin(phi) cos(phi)*cos(theta)];
T_B_I = simplify(T_I_B^-1);

%% simulation + system design
close all;
clear all;

g = 9.8; % m/s^2
% values grabbed from Intel Aero RTF CAD model
m = 0.865; % kg
Jx = 7.213e-2; % kg*m^2
Jy = 4.479e-2; % kg*m^2
Jz = 9.340e-2; % kg*m^2
b = 1;
d = 1;
l = 0.362; % length between opposite propellers

A = [zeros(3) zeros(3,1) zeros(3,1) zeros(3,1) eye(3) zeros(3);
    zeros(3) zeros(3,1) zeros(3,1) zeros(3,1) zeros(3) eye(3);
    zeros(1,3) 0 -g 0 zeros(1,3) zeros(1,3);
    zeros(1,3) g 0 0 zeros(1,3) zeros(1,3);
    zeros(4,3) zeros(4,1) zeros(4,1) zeros(4,1) zeros(4,3) zeros(4,3)];

B = [zeros(8,1) zeros(8,1) zeros(8,1) zeros(8,1);
    -1/m 0 0 0;
    0 1/Jx 0 0;
    0 0 1/Jy 0;
    0 0 0 1/Jz];

% check controllability
ctrb_mat = ctrb(A,B);
% C is full rank (12), so controllable
rank_C = rank(ctrb_mat);

C = [eye(3) zeros(3,9);
    0 0 0 0 0 1 0 0 0 0 0 0];

% check observability
obsv_mat = obsv(A,C);
% O is full rank (12), so observable
rank_O = rank(obsv_mat);

% natural dynamics
sys_ol = ss(A, B, C, 0);
x0 = [1 2 3 pi/18 pi/18 0 0.3 0.4 0.5 0.1 0.2 0.3];
figure();
initial(sys_ol, x0);
title('Open-Loop Initial Response');
grid on;

% pole placement
poles = [-5+1i,-5-1i,-5+2i,-5-2i,-5+3i,-5-3i,...
    -6+1i,-6-1i,-6+2i,-6-2i,-6+3i,-6-3i];
K = place(A, B, poles);
sys_cl = ss(A-B*K, [], C, 0);
figure();
initial(sys_cl, x0);
title('Closed-Loop Initial Response');
grid on;

%% LQR design
R = 100*eye(4);
Q1 = 0.1*eye(12);
Q2 = eye(12);
Q3 = 10*eye(12);

K1 = lqr(sys_ol, Q1, R);
K2 = lqr(sys_ol, Q2, R);
K3 = lqr(sys_ol, Q3, R);

sys1 = ss(A-B*K1, [], C, 0);
sys2 = ss(A-B*K2, [], C, 0);
sys3 = ss(A-B*K3, [], C, 0);

runs = 10;
for i = 1:runs
    xi(12*(i-1)+1:12*i) = [rand rand rand pi*rand/18 pi*rand/18 pi*rand/18 ...
        rand rand rand rand/2 rand/2 rand/2];
end
figure();
hold on;
grid on;
for i = 1:runs
    x_i = xi(12*(i-1)+1:12*i);
    [y,t,x] = initial(sys1, x_i);
    plot(t, x(:,1), 'r-');
    [y,t,x] = initial(sys2, x_i);
    plot(t, x(:,1), 'g-');
    [y,t,x] = initial(sys3, x_i);
    plot(t, x(:,1), 'b-');
end
title('X Initial Response');
xlim([0 10]);
xlabel('Time (seconds)');
ylabel('Amplitude (m)');
legend('Controller 1', 'Controller 2', 'Controller 3');

figure();
hold on;
grid on;
for i = 1:runs
    x_i = xi(12*(i-1)+1:12*i);
    [y,t,x] = initial(sys1, x_i);
    plot(t, x(:,2), 'r-');
    [y,t,x] = initial(sys2, x_i);
    plot(t, x(:,2), 'g-');
    [y,t,x] = initial(sys3, x_i);
    plot(t, x(:,2), 'b-');
end
title('Y Initial Response');
xlim([0 10]);
xlabel('Time (seconds)');
ylabel('Amplitude (m)');
legend('Controller 1', 'Controller 2', 'Controller 3');

figure();
hold on;
grid on;
for i = 1:runs
    x_i = xi(12*(i-1)+1:12*i);
    [y,t,x] = initial(sys1, x_i);
    plot(t, x(:,3), 'r-');
    [y,t,x] = initial(sys2, x_i);
    plot(t, x(:,3), 'g-');
    [y,t,x] = initial(sys3, x_i);
    plot(t, x(:,3), 'b-');
end
title('Z_{bar} Initial Response');
xlim([0 30]);
xlabel('Time (seconds)');
ylabel('Amplitude (m)');
legend('Controller 1', 'Controller 2', 'Controller 3');

figure();
hold on;
grid on;
for i = 1:runs
    x_i = xi(12*(i-1)+1:12*i);
    [y,t,x] = initial(sys1, x_i);
    plot(t, x(:,6), 'r-');
    [y,t,x] = initial(sys2, x_i);
    plot(t, x(:,6), 'g-');
    [y,t,x] = initial(sys3, x_i);
    plot(t, x(:,6), 'b-');
end
title('\psi Initial Response');
xlim([0 10]);
xlabel('Time (seconds)');
ylabel('Amplitude (rad)');
legend('Controller 1', 'Controller 2', 'Controller 3');

cont = K3;
% observer design
e = eig(A-B*cont);
factor = 1;
poles = [e(1)*factor e(2)*factor e(3)*factor e(4)*factor e(5)*factor ...
    e(6)*factor e(7)*factor e(8)*factor e(9)*factor e(10)*factor ...
    e(11)*factor e(12)*factor];
K_l = place(A', C', poles);
L = K_l';

% A matrix for x and e
% Ao = [A-B*K3 -B*K3;
%     zeros(size(A)) A-L*C];
% A matrix for x and x_hat
Ao = [A -B*cont;
    L*C A-B*cont-L*C];
Bo = [B; zeros(size(B))];
Co = [C zeros(size(C))];
sys_obs = ss(Ao, Bo, Co, 0);
co = 1/10;
x0_xhat = [rand rand rand pi*rand/18 pi*rand/18 pi*rand/18 ...
        rand rand rand rand/2 rand/2 rand/2];
x0_obs = [[rand rand rand pi*rand/18 pi*rand/18 pi*rand/18 ...
        rand rand rand rand/2 rand/2 rand/2] [x0_xhat]];
[y_obs, t_obs, x_obs] = initial(sys_obs, x0_obs);
% figure();
% initial(sys_obs, x0_obs);
% grid on;

% compare with outputs measurable
x0_fee = x0_obs(1:12);
sys_fee = ss(A-B*cont, [], C, 0);
[y_fee, t_fee, x_fee] = initial(sys_fee, x0_fee);

% plot
figure();
hold on;
plot(t_obs, x_obs(:,1), 'Color', [0, 0.4470, 0.7410], 'LineStyle', '--', 'LineWidth', 1.1);
plot(t_fee, x_fee(:,1), 'Color', [0, 0.4470, 0.7410], 'LineStyle', '-', 'LineWidth', 1.1);

plot(t_obs, x_obs(:,2), 'Color', [0.8500, 0.3250, 0.0980], 'LineStyle', '--', 'LineWidth', 1.1);
plot(t_fee, x_fee(:,2), 'Color', [0.8500, 0.3250, 0.0980], 'LineStyle', '-', 'LineWidth', 1.1);

plot(t_obs, x_obs(:,3), 'Color', [0.9290, 0.6940, 0.1250], 'LineStyle', '--', 'LineWidth', 1.1);
plot(t_fee, x_fee(:,3), 'Color', [0.9290, 0.6940, 0.1250], 'LineStyle', '-', 'LineWidth', 1.1);

plot(t_obs, x_obs(:,6), 'Color', [0.4940, 0.1840, 0.5560], 'LineStyle', '--', 'LineWidth', 1.1);
plot(t_fee, x_fee(:,6), 'Color', [0.4940, 0.1840, 0.5560], 'LineStyle', '-', 'LineWidth', 1.1);
legend('State Observer (X)', 'State Feedback (X)',...
    'State Observer (Y)', 'State Feedback (Y)',...
    'State Observer (Z_{bar})', 'State Feedback (Z_{bar})',...
    'State Observer (\psi)', 'State Feedback (\psi)');
xlabel('Time (seconds)');
ylabel('Amplitude');
title('State Observer States vs. State Feedback States vs. Time');
grid on;