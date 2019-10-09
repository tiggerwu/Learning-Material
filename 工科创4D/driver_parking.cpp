/*
WARNING !
DO NOT MODIFY CODES BELOW!
*/

#include <iostream>


#ifdef _WIN32
#include <windows.h>
#endif

#include <math.h>
#include "driver_parking.h"
using std::cout;
using std::endl;
void getpointlinedist();
void getAngle();
float square_sum(float a, float b);
float dist(float x1, float x2, float y1, float y2);
float getR(float x1, float x2, float x3, float y1, float y2, float y3);
double getError(float mid[][2], float bias);
int sgn(int a);
static void userDriverGetParam(float lotX, float lotY, float lotAngle, bool bFrontIn, float carX, float carY, float caryaw, float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm);
static void userDriverSetParam(bool* bFinished, float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear);
static int InitFuncPt(int index, void *pt);

// Module Entry Point
extern "C" int driver_parking(tModInfo *modInfo)
{
	memset(modInfo, 0, 10 * sizeof(tModInfo));
	modInfo[0].name = "driver_parking";	// name of the module (short).
	modInfo[0].desc = "user module for CyberParking";	// Description of the module (can be long).
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
	printf("OK!\n");
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
static float curv1, curv2; //曲率
static float _yaw, _yawrate, _speed, _acc, _width, _rpm, _lotX, _lotY, _lotAngle, _carX, _carY, _caryaw;
static int _gearbox, w = 0;
static bool _bFrontIn;
static float targX, targY, dist_targ, angle, dis_point_line, m;
static float dis_point_line_array[5], avepointlinelist, dangle[5], aveangle;
static int back = 0;
static float speed;
float angle_err_sum = 0, dis_err_sum = 0;
static float D_err, D_err_dif, D_err_sum = 0, D_err_tmp = 0;
static float x_err, x_err_dif, x_err_sum, x_err_tmp = 0;
static int count = 0;
static float R1, R2;
int status;
static void userDriverGetParam(float lotX, float lotY, float lotAngle, bool bFrontIn, float carX, float carY, float caryaw, float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm) {
	/* write your own code here */

	_lotX = lotX;
	_lotY = lotY;      //车位中心点绝对坐标
	_lotAngle = lotAngle;//车位绝对朝向
	_bFrontIn = bFrontIn;
	_carX = carX;
	_carY = carY;     //车辆绝对坐标
	_caryaw = caryaw; //车辆绝对朝向
	float point[21][2];
	int i, j = 0;
	for (int i = 0; i < 200; ++i) _midline[i][0] = midline[i][0], _midline[i][1] = midline[i][1];
	curv1 = getR(_midline[0][0], _midline[10][0], _midline[20][0], _midline[0][1], _midline[10][1], _midline[20][1]);		//路径的曲率
	curv2 = getR(_midline[0][0], _midline[5][0], _midline[10][0], _midline[0][1], _midline[5][1], _midline[10][1]);
	R1 = 1 / curv1;
	R2 = 1 / curv2;
	_yaw = yaw;
	_yawrate = yawrate;
	_speed = speed;
	_acc = acc;
	_width = width;
	_rpm = rpm;
	_gearbox = gearbox;

	/*if (fabs(R1) < 100)
	{
	targX = lotX + 6.5*cos(_lotAngle + 0.32);			//规划路径  预瞄
	targY = lotY + 6.5*sin(_lotAngle + 0.32);
	}
	else*/

	if (fabs(R1) < 100)
	{
		targX = lotX + 6.5 * cos(_lotAngle + 0.32);
		targY = lotY + 6.5 * sin(_lotAngle + 0.32);
	}

	else if (fabs(R1) < 500)
	{
		targX = lotX + 7.9*cos(_lotAngle + 0.25);
		targY = lotY + 7.9*sin(_lotAngle + 0.25);

	}

	else
	{
		if (R1 > 0)
		{
			targX = lotX + 5.5 * cos(_lotAngle + 0.35);
			targY = lotY + 5.5 * sin(_lotAngle + 0.35);
		}
		else
		{
			targX = lotX + 7.9*cos(_lotAngle + 0.25);
			targY = lotY + 7.9*sin(_lotAngle + 0.25);
		}
	}


	if (cos(_lotAngle) >= 0) { w = -1; }
	else { w = 1; } //判断车位朝向



	dist_targ = sqrt(square_sum((_carX - targX), (_carY - targY)));//设置目标停车准备点

	dis_point_line = w * (tan(_lotAngle)*(_carX - _lotX) + (_lotY - _carY)) / (sqrt(tan(_lotAngle)*tan(_lotAngle) + 1));
	//点到直线距离公式 2.45? 车的位置到停车位所在直线的距离

	if (fabs(_lotAngle - _caryaw) <= PI) { angle = _lotAngle - _caryaw; }
	else {
		if (_lotAngle - _caryaw >= 0)
			angle = _lotAngle - _caryaw - 2 * PI;   //车辆转过angle角度，与车位方向重合
		else
			angle = _lotAngle - _caryaw + 2 * PI;
	}
}



static void userDriverSetParam(bool* bFinished, float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear)
{
	/* write your own code here */
	getpointlinedist();
	getAngle();
	avepointlinelist = (dis_point_line_array[0] + dis_point_line_array[1] + dis_point_line_array[2] + dis_point_line_array[3] + dis_point_line_array[4]) / 5;
	aveangle = (dangle[0] + dangle[1] + dangle[2] + dangle[3] + dangle[4]) / 5;

	angle_err_sum += 1 * angle;
	dis_err_sum += 1 * dis_point_line;

	if (!*bFinished) {
		//其它路段按巡线方式行驶
		status = 0;
		//cout << "0正常巡线" << endl;
		*cmdAcc = 1;//油门给100%
		*cmdBrake = 0;//无刹车
		*cmdSteer = (_yaw - 8 * atan2(_midline[30][0], _midline[30][1])) / PI;//设定舵机方向
		*cmdGear = 1;//档位始终挂1
		if (square_sum((_carX - _lotX), (_carY - _lotY)) < 3500) {                //到一定范围时，将车子调整至道路左侧		//3500与半径相关
			status = 1;																		   //cout << "1左移" << endl;
																							   /*if (_midline[0][0] < 3.5)
																							   *cmdSteer = (_yaw - 3.98 * atan2(_midline[20][0] - _width / 3, _midline[20][1])) / PI;
																							   else
																							   *cmdSteer = (_yaw - 3.98 * atan2(_midline[20][0] - _width / 3, _midline[20][1])) / PI;*/


																							   /*x_err = _midline[0][0] - 3.6;				//3.6为最佳泊车起始位置
																							   x_err_dif = x_err - x_err_tmp;
																							   x_err_sum += x_err;
																							   x_err_tmp = x_err;
																							   *cmdSteer = - 0.033 * x_err - 0.03 * x_err_dif - 0.0002 * x_err_sum;*/


																							   /*D_err = (_yaw - 1.5 * atan2(_midline[10][0] - 3.6, _midline[10][1])) / PI;
																							   D_err_dif = D_err - D_err_tmp;
																							   D_err_sum += D_err;
																							   D_err_tmp = D_err;
																							   *cmdSteer = 0.2 * D_err + 0.2 * D_err_dif + 0.005 * D_err_sum;*/

																							   /*float b = 3.6;
																							   D_err = 2 * _yaw - atan(10 * getError(_midline,b) / _speed);
																							   D_err_sum += D_err;
																							   D_err_dif = D_err - D_err_tmp;
																							   D_err_tmp = D_err;
																							   *cmdSteer = 6.2 * D_err + 1.2 * D_err_dif;*/

			*cmdSteer = (_yaw - 3.98 * atan2(_midline[20][0] - _width / 3, _midline[20][1])) / PI;



			*cmdGear = 1; *cmdAcc = 0.2; *cmdBrake = 0;
		}

		//if (square_sum((_carX - _lotX),(_carY - _lotY)) < 2500 && )


		if (dist_targ < 15) {                                                                                //右转漂移停住
			if (dist_targ > 6) {

				status = 2;
				*cmdSteer = -0.5 * fabs(atan2(targX - _carX, targY - _carY));
				if (_speed < dist_targ) { *cmdAcc = 0.3; *cmdBrake = 0; }
				else { *cmdAcc = 0; *cmdBrake = 0.2; }

			}
			if (dist_targ < 6) {
				if (fabs(R1) < 100)
				{
					//
					status = 3;

					//*cmdGear = 2;
					*cmdSteer = 0;
					*cmdAcc = 0.0088;
					*cmdBrake = 0.95;
				}

				else if (fabs(R1) > 500)
				{
					status = 3;

					*cmdSteer = 0;

					//*cmdGear = 2;
					*cmdAcc = 0.02;
					*cmdBrake = 0.95;

				}

				else
				{
					//*cmdGear = 2;
					*cmdSteer = 0;
					*cmdAcc = 0.012;
					*cmdBrake = 0.95;
				}



				if (_speed < 3) { back = 1; }
			}
		}
		if (back) {
			status = 4;//开始倒车    

			if (abs(R1) < 200)  //（车位在直路上）		//PI控制角度与点线距离
			{
				*cmdSteer = -20.5 * angle / PI - 26.88 * aveangle / PI - 1.404 * (dis_point_line)-2.472 * avepointlinelist;
				//*cmdSteer = -20.4 * angle / PI - 26.93 * aveangle / PI - 1.404 * (dis_point_line)-2.472 * avepointlinelist;
			}

			else  //（车位在弯道上）
			{
				//*cmdSteer = -21.09*angle / PI - 26.88*aveangle / PI - 1.404*(dis_point_line)-2.472 * avepointlinelist;
				*cmdSteer = -21.09 * angle / PI - 26.88 * aveangle / PI - 1.404 * (dis_point_line)-2.472 * avepointlinelist;

				//*cmdSteer = -25 * angle / PI - 0.4 * angle_err_sum / PI - 1 * dis_point_line - 0 * dis_err_sum;
			}

			/*if (abs(R1) > 500)
			{
			if (fabs(_speed) > 5.0 * sqrt(square_sum((_carX - _lotX), (_carY - _lotY))) + 4.4)
			{
			*cmdBrake = 0.3; *cmdGear = -1; *cmdAcc = 0;
			}//倒车速度控制
			else {
			*cmdBrake = 0.0; *cmdGear = -1; *cmdAcc = 0.55;
			}
			}
			else
			{*/
			if (fabs(_speed) > 4.2 * sqrt(square_sum((_carX - _lotX), (_carY - _lotY))) + 5.15)
			{
				*cmdBrake = 0.2; *cmdGear = -1; *cmdAcc = 0;
			}//倒车速度控制
			else {
				*cmdBrake = 0.0; *cmdGear = -1; *cmdAcc = 0.55;
			}
			//}

			if (square_sum((_carX - _lotX), (_carY - _lotY)) < 0.01) {                    //停住   
				status = 5;
				*cmdSteer = -33.6*angle / PI - 2.16*(dis_point_line);
				*cmdBrake = 1.0; *cmdGear = -1; *cmdAcc = 0.0;
				if (fabs(_speed) < 0.2)  *bFinished = true;
			}


		}
	}
	if (*bFinished)
	{


		if (square_sum((_carX - _lotX), (_carY - _lotY)) < 0.05)			//OK！
		{

			status = 6;//cout << "6停车完成，开始驶离" << endl;
			*cmdSteer = 0; *cmdAcc = 1; *cmdBrake = 0; *cmdGear = 1;
		}
		else
		{
			//cout << "7驶离" << endl;
			status = 7;
			*cmdBrake = 0;
			*cmdGear = 1;
			if (fabs(R1) < 110)
			{
				*cmdSteer = (_yaw - 8 * atan2(_midline[20][0], _midline[20][1])) / PI;
				*cmdAcc = 1 - 0.01 * fabs(_yawrate*_speed);
			}
			else if (fabs(R1) > 500)
			{
				*cmdSteer = (_yaw - 8 * atan2(_midline[10][0], _midline[10][1])) / PI;
				*cmdAcc = 1 - 0.013 * fabs(_yawrate*_speed);
			}
			else
			{
				*cmdSteer = (_yaw - 8 * atan2(_midline[5][0], _midline[5][1])) / PI;
				*cmdAcc = 1 - 0.01 * fabs(_yawrate*_speed);
			}

			/*if (fabs(R1) < 100)
			{
			*cmdSteer = 0.5*_yaw - 0.05*_yawrate;
			*cmdAcc = 1 - 0.001*fabs(_yawrate*_speed);
			}*/

		}
	}
	if (*cmdAcc > 1) { *cmdAcc = 1; }
	if (*cmdAcc < 0) { *cmdAcc = 0; }
	if (*cmdBrake > 1) { *cmdBrake = 1; }
	if (*cmdBrake < 0) { *cmdBrake = 0; }
	if (*cmdSteer > 1) { *cmdSteer = 1; }
	if (*cmdSteer < -1) { *cmdSteer = -1; }
	switch (status)
	{
		//case 0:cout << "巡线" << endl; break;
	case 1:cout << "左移" << endl; break;
	case 2:cout << "漂移" << endl; break;
	case 3:cout << "漂移刹车" << endl; break;
	case 4:cout << "后退" << endl; break;
	case 5:cout << "停车" << endl; break;
	case 6:cout << "停车完毕，加速" << endl; break;
	case 7:cout << "驶离" << endl; break;
	}
	/*cout << "停车位: （" << _lotX <<"," <<_lotY<<"）"<<endl;
	cout << "目标点：（" << targX << "," << targY << "）" << endl;
	cout << "停车角：" << _lotAngle << endl;
	cout << "当前位置：(" << _carX << "," << _carY << ")" << endl;*/
	//cout <<"远曲率:"<< curv1 << "近曲率：" << curv2 << endl;
	//cout << "近半径：" << R1 << "远半径：" << R2 << endl;
	//cout << "转向:" << *cmdSteer<<endl;*/
	//cout << "车坐标:" << _carX << "," << _carY << endl;
	//cout << "车朝向：" << _caryaw << endl;
	//cout << "误差:" << angle << " " << dis_point_line<<endl;
	//cout << "车到目标点的矢量：(" << targX - _carX << "," << targY - _carY << ")" << endl;
	/*cout << "车到中线的距离:" << _midline[0][0] << endl;
	cout << "车到车位的矢量：" << _lotX - _carX << "," << _lotY - _carY << endl;
	cout << "点到直线距离:" << dis_point_line << endl;
	cout << "车与车位的夹角:" << angle * 180 / PI << endl;
	cout << "当前车速：" << _speed << endl;*/
	count++;




}
void getpointlinedist() {
	int i;
	for (i = 0; i < 4; i++) {
		dis_point_line_array[i] = dis_point_line_array[i + 1];
	}
	dis_point_line_array[4] = dis_point_line;
}
void getAngle() {
	int i;
	for (i = 0; i < 4; i++) {
		dangle[i] = dangle[i + 1];
	}
	dangle[4] = angle;
}

float dist(float x1, float x2, float y1, float y2)                   //计算距离
{
	return sqrt((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1));
}
float getR(float x1, float x2, float x3, float y1, float y2, float y3)  //计算曲率
{
	float s, a, b, c;
	s = -((x2 - x1)*(y3 - y1) - (x3 - x1)*(y2 - y1)) / 2;
	a = dist(x1, x2, y1, y2);
	b = dist(x1, x3, y1, y3);
	c = dist(x3, x2, y3, y2);
	return 4 * s / (a*b*c);
}

float square_sum(float a, float b)
{
	return a * a + b * b;
}

double getError(float mid[][2], float bias)
{
	double minerror = 10000;
	for (int i = 0; i < 200; i++)
	{
		if (square_sum(mid[i][0] - bias, mid[i][1]) < minerror)
			minerror = square_sum(mid[i][0] - bias, mid[i][1]) * sgn(mid[i][0] - bias);
	}
	return minerror;
}

int sgn(int a)
{
	if (a > 0) return 1;
	else return -1;
}