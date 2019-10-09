/*
WARNING !
DO NOT MODIFY CODES BELOW!
*/
#include <iostream>
using  std::cout;
using  std::endl;
#ifdef _WIN32
#include <windows.h>
#endif

#include "driver_cruise.h"
#include "stdio.h"
#include<cmath>
#define PI 3.141592653589793238462643383279

static void userDriverGetParam(float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm);
static void userDriverSetParam(float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear);
static int InitFuncPt(int index, void *pt);

double getError(float mid[][2]);
double distance(float a, float b);
int sgn(float x);
bool IsStraight(float radius[26]);
double k = 0;

// Module Entry Point
extern "C" int driver_cruise(tModInfo *modInfo)
{
	memset(modInfo, 0, 10 * sizeof(tModInfo));
	modInfo[0].name = "driver_cruise";	// name of the module (short).
	modInfo[0].desc = "user module for CyberCruise";	// Description of the module (can be long).
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

//**********Global variables for vehicle states*********//
static float _midline[200][2];
static double radius[21];
static float _yaw, _yawrate, _speed, _acc, _width, _rpm;//
static int _gearbox;                                    //
static long int count = 0;
//******************************************************//


bool parameterSet = false;								//
void PIDParamSetter();									//
bool flag1 = true;    //when you are in highway,flag1 changes to true
double targX, targY;

//******************************************************//
typedef struct Circle									//
{														//
	double r;											//
	int sign;											//
}circle;												//
														//******************************************************//

														//********************PID parameters*************************//
double kp_s;	//kp for speed							     //
double ki_s;	//ki for speed							     //
double kd_s;	//kd for speed							     //
double kp_d;	//kp for direction						     //
double ki_d;	//ki for direction					    	 //
double kd_d;	//kd for direction						     //
				// Direction Control Variables						         //
double D_err;//direction error					             //
double D_errDiff = 0;//direction difference(Differentiation) //
double D_errSum = 0;//sum of direction error(Integration)      //
					// Speed Control Variables								     //
circle c;												     //
circle c1;												     //
circle c2;
circle c3;//
double expectedSpeed;//      							     //
double curSpeedErr;//speed error   		                     //
double speedErrSum = 0;//sum of speed error(Integration)       //
int startPoint;											     //
int delta = 4;												//
static int roadTypeJudge = 0;										//
																	//***********************************************************//

																	//*******************Other parameters*******************//
const int topGear = 6;									//
double tmp;												//
bool flag = true;											//
double offset = 0;										//
double Tmp = 0;
bool flag2 = false;
//******************************************************//

//******************************Helping Functions*******************************//
// Function updateGear:															//
//		Update Gear automatically according to the current speed.				//
//		Implemented as Schmitt trigger.											//
void updateGear(int *cmdGear);													//
																				// Function constrain:															//
																				//		Given input, outputs value with boundaries.								//
double constrain(double lowerBoundary, double upperBoundary, double input);		//
																				// Function getR:																//
																				//		Given three points ahead, outputs a struct circle.						//
																				//		{radius:[1,500], sign{-1:left,1:right}									//
circle getR(float x1, float y1, float x2, float y2, float x3, float y3);		//
																				//******************************************************************************//

static void userDriverGetParam(float midline[200][2], float yaw, float yawrate, float speed, float acc, float width, int gearbox, float rpm) {
	/* write your own code here */

	for (int i = 0; i < 200; ++i) _midline[i][0] = midline[i][0], _midline[i][1] = midline[i][1];
	_yaw = yaw;
	_yawrate = yawrate;
	_speed = speed;
	_acc = acc;
	_width = width;
	_rpm = rpm;
	_gearbox = gearbox;
	/*int j = 0;
	while (j < 26) {
	c = getR(_midline[10 * j][0], _midline[10 * j][1], _midline[10 * (j + 1)][0], _midline[10 * (j + 1)][1], _midline[10 * (j + 2)][0], _midline[10 * (j + 2)][1]);
	radius[j] = c.r;
	j++;
	}*/

}

static void userDriverSetParam(float* cmdAcc, float* cmdBrake, float* cmdSteer, int* cmdGear) {
	//this part judges the road condition

	++roadTypeJudge;
	if (roadTypeJudge == 100)
	{
		if (_speed < 24) flag1 = false;
	}



	if (parameterSet == false)		// Initialization Part
	{
		PIDParamSetter();
	}
	else
	{
		// Speed Control
		/*
		You can modify the limited speed in this module
		Enjoy  -_-
		*/
		if (flag1 == true)//highway
		{
			startPoint = _speed * 0.15;
			c1 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + delta][0], _midline[startPoint + delta][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1]);
			startPoint = _speed * 0.60;
			c2 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1], _midline[startPoint + 4 * delta][0], _midline[startPoint + 4 * delta][1]);

			c.r = min(c1.r, c2.r);
			double dis = getError(_midline);
			dis = abs(dis);
			double threshold = 0.5;
			/*if (abs(_yawrate) > 1)
			{
			expectedSpeed = 54;
			}
			else*/ {

				if (c.r < 35)
					if (dis > threshold)
						expectedSpeed = 65;
					else
						expectedSpeed = 60;
				else if (c.r < 50)
					if (dis > threshold)
						expectedSpeed = 75;
					else
						expectedSpeed = 70;
				else if (c.r < 100)
				{
					if (dis > threshold)
						expectedSpeed = 80;
					else
						expectedSpeed = 75;
				}
				else if (c.r < 135)
					if (dis > threshold)
						expectedSpeed = 82;
					else
						expectedSpeed = 77;
				else if (c.r < 160)
				{
					if (dis > threshold)
						expectedSpeed = 85;
					else
						expectedSpeed = 80;
				}
				else if (c.r < 200)
					if (dis > threshold)
						expectedSpeed = 85;
					else
						expectedSpeed = 80;
				else if (c.r < 310)
				{
					if (dis > threshold)
						expectedSpeed = 85;
					else
						expectedSpeed = 80;
				}
				else if (c.r < 450)
				{
					if (dis > threshold)
						expectedSpeed = 120;
					else
						expectedSpeed = 115;
				}
				else if (dis > threshold)
					expectedSpeed = 130;
				else
					expectedSpeed = 125;
			}

			curSpeedErr = expectedSpeed - _speed;
			speedErrSum = 0.1 * speedErrSum + curSpeedErr;
			if (_speed < 40) *cmdAcc = 1;

			else if (curSpeedErr > 0)
			{

				if (abs(*cmdSteer) < 0.7 && abs(*cmdSteer) > 0.15)
				{
					*cmdAcc = constrain(0.0, 1.0, 0.005 * curSpeedErr + ki_s * speedErrSum);
					*cmdBrake = 0;
				}
				else if (abs(*cmdSteer) > 0.7)
				{
					*cmdAcc = 0.003;
					*cmdBrake = 0;
				}

				else
				{
					*cmdAcc = 0.6;
					*cmdBrake = 0;
				}

			}
			else if (curSpeedErr < 0)
			{
				*cmdBrake = constrain(0.0, 1.0, -0.08 * curSpeedErr*0.56);
				*cmdAcc = 0;
			}

			updateGear(cmdGear);

			/******************************************Modified by Yuan Wei********************************************/
			/*
			Please select a error model and coding for it here, you can modify the steps to get a new 'D_err',this is just a sample.
			Once you have chose the error model , you can rectify the value of PID to improve your control performance.
			Enjoy  -_-
			*/
			// Direction Control		
			//set the param of PID controller
			kp_d = 4.4;
			ki_d = 0;
			kd_d = 1.4;





			if (abs(getError(_midline)) > 0.1) D_err = 2 * _yaw - atan(20 * getError(_midline) / _speed) - 0.35 * atan2(_midline[3][0], _midline[3][1]);


			else if (abs(getError(_midline)) > 0.01) D_err = 2 * _yaw - atan(70 * getError(_midline) / _speed) - 0.65 * atan2(_midline[3][0], _midline[3][1]);

			else									 D_err = 1.6 * _yaw - 1.6 * atan(170 * getError(_midline) / _speed) - 0.5 * atan2(_midline[4][0], _midline[4][1]);
			//the differential and integral operation 
			D_errDiff = D_err - Tmp;
			D_errSum = D_errSum + D_err;
			Tmp = D_err;

			//set the error and get the cmdSteer

			/*if (abs(getError(_midline)) > 0.1)*/
				*cmdSteer = constrain(-1.0, 1.0, kp_d * D_err + ki_d * D_errSum + kd_d * D_errDiff);

			/*else if (abs(getError(_midline)) > 0.01)
				*cmdSteer = constrain(-1.0, 1.0, 4.4 * D_err + ki_d * D_errSum + 1.4 * D_errDiff);

			else
				*cmdSteer = constrain(-1.0, 1.0, 4.4 * D_err + ki_d * D_errSum + 1.4 * D_errDiff);*/

			/*	double tmp_dis = 0;
			double cur_x = 0;
			double dis_dif = _midline[0][0] - tmp_dis;
			tmp_dis = _midline[0][0];
			D_err = _yaw - 5 * atan2(_midline[3][0], _midline[3][1]) + 2.0 * atan(20 * offset / _speed);
			D_errDiff = D_err - Tmp;
			D_errSum = D_errSum + D_err;
			Tmp = D_err;
			if (_speed > 100 && _midline[0][0] > 0.25)						//针对CG1一段小弯 别的赛道可能出现问题
			{
			*cmdSteer = constrain(-1.0, 1.0, 1.2 * D_err + ki_d * D_errSum + 0.1 * D_errDiff);
			}
			else if (_speed > 100 && abs(_midline[0][0]) < 0.01)
			{
			*cmdSteer = constrain(-1.0, 1.0, 1.4 * D_err + 0 * D_errSum + 0.3 * D_errDiff);
			}
			else if (_speed > 50 && abs(_midline[0][0]) > 0.02)
			*cmdSteer = constrain(-1.0, 1.0, 1.4 * D_err + 0 * D_errSum + 0.3 * D_errDiff - 1.0 * dis_dif);
			else if (_speed > 50)
			*cmdSteer = constrain(-1.0, 1.0, 1.4 * D_err + ki_d * D_errSum + 0.1 * D_errDiff - 0.7 * dis_dif);
			else
			*cmdSteer = constrain(-1.0, 1.0, 1.4 * D_err + ki_d * D_errSum + 0.1 * D_errDiff);*/

		}
		if (flag1 == false)//dirty
		{
			//printf("flag: %d", flag1);
			startPoint = _speed * 0.25;
			c1 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + delta][0], _midline[startPoint + delta][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1]);
			startPoint = _speed * 0.60;
			c2 = getR(_midline[startPoint][0], _midline[startPoint][1], _midline[startPoint + 2 * delta][0], _midline[startPoint + 2 * delta][1], _midline[startPoint + 4 * delta][0], _midline[startPoint + 4 * delta][1]);

			c.r = min(c1.r, c2.r);
			if (abs(_yawrate) > 0.9)
			{
				expectedSpeed = 54;
			}
			else
			{
				double dis = getError(_midline);
				dis = abs(dis);
				double threshold = 0.01;
				if (c.r < 40)
					/*if (dis > threshold)
						expectedSpeed = 30;
					else*/
					expectedSpeed = 60;
				else if (c.r < 80)
					/*if (dis > threshold)
						expectedSpeed = 40;
					else*/
					expectedSpeed = 60;
				else if (c.r < 100)
				{
					/*if (dis > threshold)
						expectedSpeed = 55;
					else*/
					expectedSpeed = 63;
				}
				else if (c.r < 160)
				{
					/*if (dis > threshold)
						expectedSpeed = 60;
					else*/
					expectedSpeed = 70;
				}
				else if (c.r < 310)
				{
					/*if (dis > threshold)
						expectedSpeed = 70;
					else*/
					expectedSpeed = 80;
				}
				else if (c.r < 450)
					/*if (dis > threshold)
						expectedSpeed = 90;
					else*/
					expectedSpeed = 90;
				else
				{
					/*if (dis > threshold)
						expectedSpeed = 90;
					else*/
					expectedSpeed = 100;
				}

			}
			curSpeedErr = expectedSpeed - _speed;
			speedErrSum = 0.1 * speedErrSum + curSpeedErr;
			if (_speed < 40) *cmdAcc = 1;

			else if (curSpeedErr > 0)
			{

				if (abs(*cmdSteer) < 0.7 && abs(*cmdSteer) > 0.15)
				{

					*cmdAcc = constrain(0.0, 1.0, 0.005 * curSpeedErr + ki_s * speedErrSum);
					*cmdBrake = 0;
				}
				else if (abs(*cmdSteer) > 0.7)
				{
					*cmdAcc = 0.004;
					*cmdBrake = 0;
				}
				else
				{
					*cmdAcc = 0.60;
					*cmdBrake = 0;
				}

			}
			else if (curSpeedErr < 0)
			{
				*cmdBrake = constrain(0.0, 1.0, -0.08 * curSpeedErr*0.56);
				*cmdAcc = 0;
			}

			updateGear(cmdGear);


			kp_d = 5;
			ki_d = 0;
			kd_d = 1.3;



			{
				if (abs(getError(_midline)) > 1) D_err = 2 * _yaw - atan(5 * getError(_midline) / _speed) - 0.4 * atan2(_midline[3][0], _midline[3][1]);

				else if (abs(getError(_midline)) > 0.1) D_err = 2 * _yaw - atan(15 * getError(_midline) / _speed) - 0.3 * atan2(_midline[3][0], _midline[3][1]);

				else if (abs(getError(_midline)) > 0.03)
					D_err = 2 * _yaw - atan(60 * getError(_midline) / _speed) - 0.8 * atan2(_midline[3][0], _midline[3][1]);

				else D_err = 2 * _yaw - atan(90 * getError(_midline) / _speed) - 0.5 * atan2(_midline[3][0], _midline[3][1]);

				//only track the aiming point on the middle line

				//the differential and integral operation 
				D_errDiff = D_err - Tmp;
				D_errSum = D_errSum + D_err;
				Tmp = D_err;

				//set the error and get the cmdSteer

				*cmdSteer = constrain(-1.0, 1.0, kp_d * D_err + ki_d * D_errSum + kd_d * D_errDiff);
			}
		}




		//print some useful info on the terminal
		//printf("D_err : %f \n", D_err);
		//printf("cmdSteer %f \n", *cmdSteer);
		//printf("cmdacc %f \n", *cmdAcc);
		//printf("cmdspeed %f \n", _speed);
		//printf("cmdyawrate %f \n", yawrate);
		//printf("count %f \n", count);
		//printf("", c.r);
		//printf("yaw %f \n", _yaw);
		//cout << "acc" << *cmdAcc << endl;
		//cout << count <<' '<<_speed<< endl;
		//cout << _width << endl;
		//if (c.r != 500) cout << c.r << endl;
		//cout << flag1 << endl;
		cout << "Error:" << getError(_midline) << "Speed:" << _speed << "Steer:" << *cmdSteer << "R:" << c.r << endl;
		/******************************************End by Yuan Wei********************************************/
	}
}

void PIDParamSetter()
{

	kp_s = 0.005;
	ki_s = 0;
	kd_s = 0;
	kp_d = 1.35;
	ki_d = 0.151;
	kd_d = 0.10;
	parameterSet = true;

}

void updateGear(int *cmdGear)
{
	if (_gearbox == 1)
	{
		if (_speed >= 60.2 && topGear > 1)
		{
			*cmdGear = 2;
		}
		else
		{
			*cmdGear = 1;
		}
	}
	else if (_gearbox == 2)
	{
		if (_speed <= 42.6)
		{
			*cmdGear = 1;
		}
		else if (_speed >= 106.6 && topGear > 2)
		{
			*cmdGear = 3;
		}
		else
		{
			*cmdGear = 2;
		}
	}
	else if (_gearbox == 3)
	{
		if (_speed <= 90.1)
		{
			*cmdGear = 2;
		}
		else if (_speed >= 146.1 && topGear > 3)
		{
			*cmdGear = 4;
		}
		else
		{
			*cmdGear = 3;
		}
	}
	else if (_gearbox == 4)
	{
		if (_speed <= 130.1)
		{
			*cmdGear = 3;
		}
		else if (_speed >= 187.9 && topGear > 4)
		{
			*cmdGear = 5;
		}
		else
		{
			*cmdGear = 4;
		}
	}
	else if (_gearbox == 5)
	{
		if (_speed <= 171.7)
		{
			*cmdGear = 4;
		}
		else if (_speed >= 234.3 && topGear > 5)
		{
			*cmdGear = 6;
		}
		else
		{
			*cmdGear = 5;
		}
	}
	else if (_gearbox == 6)
	{
		if (_speed <= 217.8)
		{
			*cmdGear = 5;
		}
		else
		{
			*cmdGear = 6;
		}
	}
	else
	{
		*cmdGear = 1;
	}
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


double getError(float mid[][2])
{
	double minerror = 10000;
	for (int i = 0; i < 200; i++)
	{
		if (distance(mid[i][0], mid[i][1]) < minerror)
			minerror = distance(mid[i][0], mid[i][1])*sgn(mid[i][0]);
	}
	return minerror;
}

double distance(float a, float b)
{
	return sqrt(a * a + b * b);
}

int sgn(float x)
{
	if (x > 0)
		return 1;
	else
		return -1;
}
bool IsStraight(float radius[26])
{
	int j = 0;
	for (int i = 0; i < 26; i++)
	{
		if (radius[i] != 500) break;
		else j++;
	}
	if (j == 26) return true;
	else return false;
}
