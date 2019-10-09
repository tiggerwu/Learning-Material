/*

WARNING !



DO NOT MODIFY CODES BELOW!

*/

#include<iostream>

#ifdef _WIN32

#include <windows.h>

#include <cmath>

#endif



#include "driver_follow.h"

using  std::cout;

using std::endl;

double constrain(double lowerBoundary, double upperBoundary, double input);		//

																				//

typedef struct Circle									//

{														//

	double r;											//

	int sign;											//

}circle;																			//

																					//

circle getR(float x1, float y1, float x2, float y2, float x3, float y3);		//





																				//



static int num;

static void userDriverGetParam(float LeaderXY[2], float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm);

static void userDriverSetParam(float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear);

static int InitFuncPt(int index, void *pt);

void gear(int* cmdGear, float* cmdAcc, float* cmdBrake);

float square_sum(float x, float y);

float av_speed();

float av_acc();

float av_aacc();

void getspeed();

void getdist();

void getacc();

void getaacc();

void getbrake(float);

bool judge_suddenbrake();





// Module Entry Point

extern "C" int driver_follow(tModInfo *modInfo)

{

	memset(modInfo, 0, 10 * sizeof(tModInfo));

	modInfo[0].name = "driver_follow";	// name of the module (short).

	modInfo[0].desc = "user module for CyberFollower";	// Description of the module (can be long).

	modInfo[0].fctInit = InitFuncPt;			// Init function.

	modInfo[0].gfId = 0;

	modInfo[0].index = 0;

	return 0;

}



// Module interface initialization.

static int InitFuncPt(int, void *pt)

{

	tUserItf *itf = (tUserItf *)pt;

	itf->userDriverGetParam = userDriverGetParam;

	itf->userDriverSetParam = userDriverSetParam;

	return 0;

}



/*

WARNING!



DO NOT MODIFY CODES ABOVE!

*/



/*

define your variables here.

following are just examples

*/

static float _midline[200][2];

static float _yaw, _yawrate, _speed, _acc, _width, _rpm;

static int _gearbox;

static float _Leader_X, _Leader_Y;

static float distance[5], rel_v[5], rel_acc[5], rel_aacc[5], brake[8];	//距离、相对速度、相对加速度

circle c, c1, c2;

int delta = 4;

bool flag = 0;

int count = 0;

float time = 0;

bool flag_brake = 0, flag_reaction = 0, after_brake = 0;//检测是否在急刹 是否刚经历急刹过程（针对连续刹车启动的情况）

double D_err, D_errDiff, D_errSum, Tmp;

double kp_d, ki_d, kd_d;







static void userDriverGetParam(float LeaderXY[2], float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm) {

	/* write your own code here */



	_Leader_X = LeaderXY[0];

	_Leader_Y = LeaderXY[1];

	for (int i = 0; i < 200; ++i) _midline[i][0] = midline[i][0], _midline[i][1] = midline[i][1];

	_yaw = yaw;

	_yawrate = yawrate;

	_speed = speed;

	_acc = acc;

	_width = width;

	_rpm = rpm;

	_gearbox = gearbox;

	/* you can modify the print code here to show what you want */

	//printf("speed %.3f Leader XY(%.3f, %.3f)\n", _speed, _Leader_X, _Leader_Y);

}



static void userDriverSetParam(float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear) {

	/* write your own code here */

	float a, b, sum = 0;



	float safedist = 0;	//安全距离

	getspeed();



	getdist();

	getacc();

	time += 0.02;



	//safedist = -7E-09 * pow(_speed, 4) + 4E-06 * pow(_speed, 3) - 0.0005 * _speed * _speed + 0.0372 * _speed + 9.9371;				//与速度相关的函数 



	//safedist = -8.48562E-13*pow(_speed,6)+7.18743E-10*pow(_speed,5)-2.43384E-07 * pow(_speed, 4) + 4.1655E-05 * pow(_speed, 3) - 0.00355 * _speed * _speed + 0.14923 * _speed + 8.43913;

	//safedist = -1.5654E-12*pow(_speed, 6) + 1.40061E-9*pow(_speed, 5) - 4.89083E-07 * pow(_speed, 4) + 8.41838E-05 * pow(_speed, 3) - 0.0073 * _speed * _speed + 0.30827 * _speed + 6.03765;



	//safedist = 1.16416E-12*pow(_speed, 6) -8.71472E-10*pow(_speed, 5) + 2.44051E-07 * pow(_speed, 4) -3.1078E-05 * pow(_speed, 3) + 0.00186 * _speed * _speed - 0.03443 * _speed + 10.66879;

	//if (_speed > 240)safedist = 20;

	/*if (_speed < 180)

	safedist = 1.387272E-11*pow(_speed, 6) - 8.89833E-9*pow(_speed, 5) + 2.219E-06 * pow(_speed, 4) - 2.7188E-04 * pow(_speed, 3) - 0.01709 * _speed * _speed - 0.50401 * _speed + 16.13846;

	else

	safedist = 17;*/

	//safedist = -2.55296E-7 * pow(_speed, 3) + 3.17412E-4 * pow(_speed, 2) - 0.03767 * _speed + 12.32333;

	safedist = -1.69358E-13*pow(_speed, 6) + 1.52587E-10*pow(_speed, 5) - 5.93986E-08 * pow(_speed, 4) + 1.23024E-05 * pow(_speed, 3) - 0.00118 * _speed * _speed + 0.06145 * _speed + 9.13891;

	//safedist = 9.9 + 0.0379*_speed - 4.777 / pow(10.0, 4)*_speed*_speed + 3.466 / pow(10.0, 6)*pow(_speed, 3) - 6.365 / pow(10.0, 9)*pow(_speed, 4);



	/*if ( _speed < 130 && _speed > 50) safedist += 0.35;		//7号头车

	if (_speed < 50) safedist += 0.1;						//14号头车 （范围和偏置项都是随手一写 不一定要用这个 原则是保证急刹过程中的最小距离在10.3-10.5左右 应该比较稳一点）*/



	if (_speed >= 0 && _speed <= 20)	safedist += 0.9;

	if (_speed >= 20 && _speed <= 35)   safedist += 0.3;

	if (_speed > 35 && _speed <= 45)	safedist += 0.25;

	if (_speed > 45 && _speed <= 55)	safedist += 0.3;

	if (_speed > 55 && _speed <= 65)	safedist += 0.3;

	if (_speed > 65 && _speed <= 75)	safedist += 0.4;

	if (_speed > 75 && _speed <= 85)	safedist += 0.6;

	if (_speed > 85 && _speed <= 95)	safedist += 0.45;

	if (_speed > 95 && _speed <= 105)	safedist += 0.48;

	if (_speed > 105 && _speed <= 115)	safedist += 0.3;

	if (_speed > 115 && _speed <= 125)	safedist += 0.43;

	if (_speed > 125 && _speed <= 135)	safedist += 0.3;

	if (_speed > 135 && _speed <= 145)	safedist += 0.2;

	if (_speed > 145 && _speed <= 155)	safedist -= 0.05;

	if (_speed > 155 && _speed <= 165)	safedist -= 0.15;

	if (_speed > 165 && _speed <= 175)	safedist -= 0.25;

	if (_speed > 175 && _speed <= 185)	safedist -= 0.6;

	if (_speed > 185 && _speed <= 195)	safedist -= 0.65;

	if (_speed > 195 && _speed <= 205)	safedist -= 0.9;

	if (_speed > 205 && _speed <= 215)	safedist -= 1.1;

	if (_speed > 215 && _speed <= 225)	safedist -= 1.2;

	if (_speed > 225 && _speed <= 235)	safedist -= 1.5;

	if (_speed > 235 && _speed <= 245)	safedist -= 1.2;

	if (_speed > 245 && _speed <= 255)	safedist -= 1.0;





	/*if (_speed>240&&*cmdBrake > 0.5)

	{

	flag = 1;

	count = 130;

	}

	cout << flag<<" "<<*cmdBrake<<" "<<safedist<< " "<<rel_acc[4]<<endl;



	if (flag)

	{

	safedist +=1 ;

	count--;

	}



	if (count == 0)flag = 0;*/





	//cout << safedist<<endl;

	double k_v1, k_v2, k_acc, k_sum, k_dis, k_aacc;



	k_v1 = 2.0;

	k_v2 = 2.0;				//speed 会不会有问题？

	k_acc = 0.2;			//针对急刹

	k_sum = 0.6;

	k_dis = 0.8;

	//k_aacc = 4;



	float tmp_Y = 0, error_Y = 0, error_Y_sum = 0, error_Y_dif = 0;

	error_Y = _Leader_Y;

	error_Y_sum = error_Y_sum + tmp_Y;

	error_Y_dif = error_Y - tmp_Y;

	tmp_Y = error_Y;





	for (int i = 0; i < 5; i++) { sum = sum + distance[i]; }

	if (rel_acc[4] > 8)

	{

		*cmdAcc = constrain(0, 1.0, k_v1 * rel_v[4] + k_acc * rel_acc[4] + k_sum * (sum / 5 - safedist) + k_dis * (distance[4] - safedist) + 0.05); //油门 刹车PID控制

		*cmdBrake = constrain(0, 1.0, -k_v2 * rel_v[4] - k_acc * rel_acc[4] - k_sum * (sum / 5 - safedist) - k_dis * (distance[4] - safedist));



	}

	else if (rel_acc[4] < -8)

	{

		*cmdAcc = constrain(0, 1.0, k_v1 * rel_v[4] + 0.5*k_acc * rel_acc[4] + k_sum * (sum / 5 - safedist) + k_dis * (distance[4] - safedist)); //油门 刹车PID控制

		*cmdBrake = constrain(0, 1.0, -k_v2 * rel_v[4] - 0.5*k_acc * rel_acc[4] - k_sum * (sum / 5 - safedist) - k_dis * (distance[4] - safedist) - 0.05);





	}



	else {



		*cmdAcc = constrain(0, 1.0, k_v1 * rel_v[4] + 0.25*k_acc * rel_acc[4] + k_sum * (sum / 5 - safedist) + k_dis * (distance[4] - safedist)); //油门 刹车PID控制

		*cmdBrake = constrain(0, 1.0, -k_v2 * rel_v[4] - 0.25*k_acc * rel_acc[4] - k_sum * (sum / 5 - safedist) - k_dis * (distance[4] - safedist));

	}







	if ((rel_acc[4] < -9) && (*cmdAcc >= 0.9))//前车突然减速，我车在加速

	{

		*cmdAcc = constrain(0, 1.0, 2 * rel_v[4] + 0.5*rel_acc[4] + 0.6*(sum / 5 - safedist) + 0.8*(distance[4] - safedist)); //油门 刹车PID控制

		*cmdBrake = constrain(0, 1.0, -2 * rel_v[4] - 1 * rel_acc[4] - 0.6*(sum / 5 - safedist) - 0.8*(distance[4] - safedist) - 0.05);



	}



	getbrake(*cmdBrake);

	flag_brake = judge_suddenbrake();

	if (flag_brake)			//如果在刹车 刹车踩满

	{

		flag_reaction = 1;

	}



	if (flag_reaction)		//在响应过程中直到前车加速 结束

	{

		*cmdBrake = 1;

		*cmdAcc = 0;

		if (rel_acc[4] > 2 || _Leader_Y > 10.5)

		{

			flag_reaction = 0;

			*cmdAcc = constrain(0, 1.0, k_v1 * rel_v[4] + 0.25*k_acc * rel_acc[4] + k_sum * (sum / 5 - safedist) + k_dis * (distance[4] - safedist)); //油门 刹车PID控制

			*cmdBrake = constrain(0, 1.0, -k_v2 * rel_v[4] - 0.25*k_acc * rel_acc[4] - k_sum * (sum / 5 - safedist) - k_dis * (distance[4] - safedist));

			after_brake = 1;

		}

	}





	if (fabs(*cmdSteer)*_speed > 50) {				//转向时速度不能太大

		*cmdAcc = constrain(0, 1.0, k_v1 * rel_v[4] + 0 * rel_acc[4] + 0.6*(sum / 5 - safedist) + 0.8*(distance[4] - safedist) - 0.04*_speed*abs(*cmdSteer));

	}











	/*

	kp_d = abs(_Leader_X) < 0.1? 60:55;



	ki_d = 0.1;



	kd_d = 100;



	D_err = -atan2(_Leader_X, _Leader_Y) / 10 * PI;



	D_errDiff = D_err - Tmp;



	D_errSum = D_errSum + D_err;



	Tmp = D_err;



	*cmdSteer = constrain(-1.0, 1.0, kp_d * D_err + ki_d * D_errSum + kd_d * D_errDiff);

	*/





	kp_d = abs(_Leader_X) < 0.1 ? 55 : 50;



	ki_d = 0.1;



	kd_d = 100;



	D_err = -atan2(_Leader_X, _Leader_Y) / 10 * PI;



	D_errDiff = D_err - Tmp;



	D_errSum = D_errSum + D_err;



	Tmp = D_err;



	*cmdSteer = constrain(-1.0, 1.0, kp_d * D_err + ki_d * D_errSum + kd_d * D_errDiff);







	/*if (c.r < 120)

	{

	*cmdSteer = constrain(-0.8, 0.8, (_yaw - 1 / (distance[4]) * 280 * atan2(1.2*_Leader_X, _Leader_Y) - 1 * atan2(_midline[20][0], _midline[20][1])) / 3.14);

	}

	else

	{

	*cmdSteer = constrain(-0.8, 0.8, (_yaw - 1 / (distance[4]) * 240 * atan2(1 * _Leader_X, _Leader_Y) - 1.9* atan2(_midline[20][0], _midline[20][1])) / 3.14);

	}*/





	/*float tmp_X = 0, error_X = 0, error_X_sum = 0, error_X_dif = 0;

	error_X = _Leader_X;

	error_X_sum = error_X_sum + tmp_X;

	error_X_dif = error_X - tmp_X;

	tmp_X = error_X;



	float kp_d1 = 0.6;

	float kd_d1 = 0.2;

	float kp_d2 = 0.45;

	float kd_d2 = 0.15;



	if (abs(_Leader_X) > 0.01)



	*cmdSteer = constrain(-0.8, 0.8, (_yaw - 1.5 * atan2(_midline[30][0], _midline[30][1])) / 3.14 - kp_d1 * error_X + kd_d1 * error_X_dif);



	else



	*cmdSteer = constrain(-0.8, 0.8, (_yaw - 8 * atan2(_midline[50][0], _midline[50][1])) / 3.14 - kp_d2 * error_X + kd_d2 * error_X_dif);*/







	if (*cmdBrake >= 0.8) { *cmdSteer = 0; }





	/*if (after_brake && time > 5)					//针对连续启动刹车的情况 刚急刹完加速度不能过大。

	{



	safedist += 1;



	if (*cmdAcc < 0.01)

	{

	after_brake = 0;

	}



	}*/







	int startPoint = _speed * 0.15;

	c1 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + delta][0], _midline[startPoint + delta][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1]);

	startPoint = _speed * 0.60;

	c2 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1], _midline[startPoint + 4 * delta][0], _midline[startPoint + 4 * delta][1]);

	c.r = min(c1.r, c2.r);

	gear(cmdGear, cmdAcc, cmdBrake);



	//cout << rel_acc[4] << " " << rel_acc[3] << " " << rel_acc[2] << " " << rel_acc[1] << " " << rel_acc[0] << endl;

	cout << "运行时间：" << time << " Leaderx:" << _Leader_X << " Leadery:" << _Leader_Y << " " << " 刹车值：" << *cmdBrake << " 油门值：" << *cmdAcc << " 是否在急刹:" << flag_reaction << " 当前速度：" << _speed << endl;



}

void gear(int* cmdGear, float* cmdAcc, float* cmdBrake) {

	if (_speed <= 45)*cmdGear = 1;

	if (_speed > 45 && _speed <= 105 && *cmdGear == 1 && _rpm > 650) *cmdGear = *cmdGear + 1;

	if (_speed > 105 && _speed <= 155 && *cmdGear == 2 && _rpm > 650) *cmdGear = *cmdGear + 1;

	if (_speed > 155 && _speed <= 195 && *cmdGear == 3 && _rpm > 650) *cmdGear = *cmdGear + 1;

	if (_speed > 195 && _speed <= 240 && *cmdGear == 4 && _rpm > 650)*cmdGear = *cmdGear + 1;

	if (_speed > 240 && *cmdGear == 5 && _rpm > 600)*cmdGear = *cmdGear + 1;

	if (_speed <= 45 && *cmdGear == 2)*cmdGear = *cmdGear - 1;

	if (_speed > 45 && _speed <= 105 && *cmdGear == 3 && _rpm < 600) *cmdGear = *cmdGear - 1;

	if (_speed > 105 && _speed <= 155 && *cmdGear == 4 && _rpm < 600) *cmdGear = *cmdGear - 1;

	if (_speed > 155 && _speed <= 195 && *cmdGear == 5 && _rpm < 600) *cmdGear = *cmdGear - 1;

	if (_speed > 195 && _speed <= 240 && *cmdGear == 6 && _rpm < 600)*cmdGear = *cmdGear - 1;

}

float square_sum(float x, float y)

{

	return sqrt(x * x + y * y);

}



void getdist() {

	int i;

	for (i = 0; i < 4; i++) {

		distance[i] = distance[i + 1];

	}

	distance[4] = square_sum(_Leader_X, _Leader_Y);

}

void getbrake(float cur_brake)

{

	int i;

	for (i = 0; i < 8; i++) {

		brake[i] = brake[i + 1];

	}

	brake[8] = cur_brake;

}

bool judge_suddenbrake()

{

	bool flag = true;

	int start = _speed > 50 ? 0 : 4;

	for (int i = start; i <= 7; ++i)

	{

		if (brake[i] < 0.6) flag = false;

	}

	return flag;

}

float av_speed() {	//平均速度

	int i;

	float vsum;

	vsum = 0;

	for (i = 3; i > 0; i = i - 1) {

		vsum = vsum + (distance[4] - distance[i]) / (0.02*(4 - i));

	}

	return vsum / 4;

}

void getspeed() {		//平均速度数组

	int i;

	for (i = 0; i < 4; i++) {

		rel_v[i] = rel_v[i + 1];

	}

	rel_v[4] = av_speed();

}

float av_acc() {	//平均加速度

	int i;

	float accsum;

	accsum = 0;

	for (i = 3; i > 0; i = i - 1) {

		accsum = accsum + (rel_v[4] - rel_v[i]) / (0.02*(4 - i));

	}

	return accsum / 4;

}

void getacc() {

	int i;

	for (i = 0; i < 4; i++)

	{

		rel_acc[i] = rel_acc[i + 1];

	}

	rel_acc[4] = av_acc();

}

float av_aacc() {

	int i;

	float aaccsum;

	aaccsum = 0;

	for (i = 3; i > 0; i = i - 1)

	{

		aaccsum = aaccsum + (rel_acc[4] - rel_acc[i]) / (0.02*(4 - i));

	}

	return aaccsum / 4;

}

void getaacc()

{

	int i;

	for (i = 0; i < 4; i++)

	{

		rel_aacc[i] = rel_aacc[i + 1];

	}

	rel_aacc[4] = av_aacc();

}

circle getR(float x1, float y1, float x2, float y2, float x3, float y3)

{

	double a, b, c, d, e, f;

	double r, x, y;



	a = 2 * (x2 - x1);

	b = 2 * (y2 - y1);

	c = x2 * x2 + y2 * y2 - x1 * x1 - y1 * y1;

	d = 2 * (x3 - x2);

	e = 2 * (y3 - y2);

	f = x3 * x3 + y3 * y3 - x2 * x2 - y2 * y2;

	x = (b*f - e * c) / (b*d - e * a);

	y = (d*c - a * f) / (b*d - e * a);

	r = sqrt((x - x1)*(x - x1) + (y - y1)*(y - y1));

	x = constrain(-1000.0, 1000.0, x);

	y = constrain(-1000.0, 1000.0, y);

	r = constrain(1.0, 500.0, r);

	int sign = (x > 0) ? 1 : -1;

	circle tmp = { r,sign };

	return tmp;

}

double constrain(double lowerBoundary, double upperBoundary, double input)

{

	if (input > upperBoundary)

		return upperBoundary;

	else if (input < lowerBoundary)

		return lowerBoundary;

	else

		return input;

}