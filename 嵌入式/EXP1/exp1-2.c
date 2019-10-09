#include <stdint.h>
#include <stdbool.h>
#include "hw_memmap.h"
#include "debug.h"
#include "gpio.h"
#include "hw_types.h"
#include "pin_map.h"
#include "sysctl.h"


#define   FASTFLASHTIME			(uint32_t) 500000
#define   SLOWFLASHTIME			(uint32_t) 4000000

uint32_t delay_time,key_value;


void 		Delay(uint32_t value);
void 		S800_GPIO_Init(void);



int main(void)
{
	
	int num=0; //����
	
	S800_GPIO_Init();
	
	while(1)                    
  {
		//key_value = GPIOPinRead(GPIO_PORTJ_BASE,GPIO_PIN_0)	;				//read the PJ0 key value  ����   

		if (GPIOPinRead(GPIO_PORTJ_BASE,GPIO_PIN_0)	== 0)				// ����һ  ��sw1 ��m0 ��Ϩ��		��sw2 ��m1 ��Ϩ��
		  { 
				GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0x1);	
		  }
    else if (GPIOPinRead(GPIO_PORTJ_BASE,GPIO_PIN_1)	== 0)	
		{
			GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_1, 0x2);
		}
		else {
			GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0|GPIO_PIN_1, 0x0);
		} 
	



		
		/*GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0x1);			// Turn on the LED.   //��˸
		Delay(delay_time);
		GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0x0);							// Turn off the LED.
		Delay(delay_time);*/
   }
}

void Delay(uint32_t value)
{
	uint32_t ui32Loop;
	for(ui32Loop = 0; ui32Loop < value; ui32Loop++){};
}


void S800_GPIO_Init(void)
{
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);						//Enable PortF
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));			//Wait for the GPIO moduleF ready

	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);						//Enable PortJ	
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));			//Wait for the GPIO moduleJ ready	
	
  GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0);			//Set PF 0123 as Output pin	
	GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_1);
	GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_2);
	GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_3);
	
	GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE,GPIO_PIN_0 | GPIO_PIN_1);//Set the PJ0,PJ1 as input pin
	//����GPIO�˿�����Ϊ�������ţ���GPIOPinTypeGPIOOutput()���ơ�GPIO_PIN_0 | GPIO_PIN_1 = 00000011b
	
	
	GPIOPadConfigSet(GPIO_PORTJ_BASE,GPIO_PIN_0 | GPIO_PIN_1,GPIO_STRENGTH_2MA,GPIO_PIN_TYPE_STD_WPU);
	//����ԭ�ͣ�void GPIOPadConfigSet(uint32_t ui32Port, uint8_t ui8Pins, uint32_t ui32Strength, uint32_t ui32PinType)
	//GPIO�˿����á�uint32_t ui32Port��GPIO�˿ڻ���ַ
	//ui8Pins���˿�����λ��ϱ�ʾ����10000001b��ʾ���ö˿ڵ�D7��D0λ
	//ui32Strength���˿ڵ��������������������������Ч����ѡ�����GPIO_STRENGTH_2MA/4MA/8MA/8MA_SC/6MA/10MA/12MA
	//ui32PinType���������ͣ���ѡ�����GPIO_PIN_TYPE_STD�����죩��GPIO_PIN_TYPE_STD_WPU��������������GPIO_PIN_TYPE_STD_WPD��������������
	//GPIO_PIN_TYPE_OD����©����GPIO_PIN_TYPE_ANALOG��ģ�⣩��GPIO_PIN_TYPE_WAKE_HIGH���ߵ�ƽ�Ӷ��߻��ѣ���GPIO_PIN_TYPE_WAKE_LOW���ͣ�
}


