
#include <stdint.h>
#include <stdbool.h>
#include "hw_memmap.h"
#include "debug.h"
#include "gpio.h"
#include "hw_i2c.h"
#include "hw_types.h"
#include "i2c.h"
#include "pin_map.h"
#include "sysctl.h"
#include "SysTick.h"
#include "interrupt.h"

//*****************************************************************************
//
//I2C GPIO chip address and resigster define
//
//*****************************************************************************
#define TCA6424_I2CADDR 					0x22
#define PCA9557_I2CADDR						0x18

#define PCA9557_INPUT							0x00
#define	PCA9557_OUTPUT						0x01
#define PCA9557_POLINVERT					0x02
#define PCA9557_CONFIG						0x03

#define TCA6424_CONFIG_PORT0			0x0c
#define TCA6424_CONFIG_PORT1			0x0d
#define TCA6424_CONFIG_PORT2			0x0e

#define TCA6424_INPUT_PORT0				0x00
#define TCA6424_INPUT_PORT1				0x01
#define TCA6424_INPUT_PORT2				0x02

#define TCA6424_OUTPUT_PORT0			0x04
#define TCA6424_OUTPUT_PORT1			0x05
#define TCA6424_OUTPUT_PORT2			0x06


#define SYSTICK_FREQUENCY					1000			//1000hz

#define	I2C_FLASHTIME							500				//500mS��I2C��ʱʱ��
#define GPIO_FLASHTIME						300				//30mS��GPIO��ʱʱ��


void 		Delay(uint32_t value);
void 		S800_Clock_Init(void);
void 		S800_GPIO_Init(void);
void		S800_I2C0_Init(void);
uint8_t I2C0_WriteByte(uint8_t DevAddr, uint8_t RegAddr, uint8_t WriteData);
uint8_t I2C0_ReadByte(uint8_t DevAddr, uint8_t RegAddr);
void 		S800_SysTick_Init(void);

uint32_t ui32SysClock;
uint8_t seg7[] = {0x3f,0x06,0x5b,0x4f,0x66,0x6d,0x7d,0x07,0x7f,0x6f,0x77,0x7c,0x58,0x5e,0x079,0x71,0x5c};

//systick software counter define
volatile uint16_t systick_10ms_couter=SYSTICK_FREQUENCY/100;	//10ms��100ms��ʱ��
volatile uint16_t systick_100ms_couter=SYSTICK_FREQUENCY/10; 	//10ms��100ms��ʱ��
volatile uint8_t	systick_10ms_status,systick_100ms_status; 	//10ms��100ms��ʱ״̬


int main(void)
{
	
	volatile uint8_t cnt=0, k=0; 
	volatile uint16_t	i2c_flash_cnt, gpio_flash_cnt;
	
	S800_Clock_Init();
	S800_GPIO_Init();
	S800_I2C0_Init();
	S800_SysTick_Init();

  IntMasterEnable();	//�������ж�ʹ��	
	
	while (1)
	{
		if (systick_10ms_status) //10ms��ʱ��
		{
			systick_10ms_status		= 0; //����10ms��ʱ״̬
			
			if (++gpio_flash_cnt >= GPIO_FLASHTIME/10)
			{
				gpio_flash_cnt			= 0;
				
				//PF0�Ʒ�ת
				GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, ~GPIOPinRead(GPIO_PORTF_BASE, GPIO_PIN_0 )); 
			}

			//���������ƣ�����10ms��ʱˢ������ܣ��������Ӿ�ͬʱ�����������ֵ��
			I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_OUTPUT_PORT2,0); //������ܣ���ֹ��Ӱ��
			if (cnt < 7 || k == 0) {
				I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_OUTPUT_PORT1,seg7[cnt+1+k]);				//write port 1 				
				I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_OUTPUT_PORT2,(uint8_t)(1<<(cnt+k)));		//write port 2
			} 
			else {
				I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_OUTPUT_PORT1,seg7[1]);				//write port 1 				
				I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_OUTPUT_PORT2,(uint8_t)(1));		//write port 2
			}
			k = 1 - k;
			
			//LED�����
				if (cnt < 7)
					I2C0_WriteByte(PCA9557_I2CADDR,PCA9557_OUTPUT,~(3<<cnt));	
				else
					I2C0_WriteByte(PCA9557_I2CADDR,PCA9557_OUTPUT,~((3<<cnt)|0x1));
			
		}
		
		if (systick_100ms_status) //100ms��ʱ��
		{
			systick_100ms_status	= 0; //����100ms��ʱ״̬
			
			if (++i2c_flash_cnt		>= I2C_FLASHTIME/100)
			{
				i2c_flash_cnt				= 0;

				if (++cnt >= 0x8)
					cnt = 0;
								

			}
		}
	}

}

void S800_Clock_Init(void)
{
	//use internal 16M oscillator, HSI
	//ui32SysClock = SysCtlClockFreqSet((SYSCTL_OSC_INT |SYSCTL_USE_OSC), 16000000);		

	//use extern 25M crystal
	//ui32SysClock = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |SYSCTL_OSC_MAIN |SYSCTL_USE_OSC), 25000000);		

	//use PLL
	//ui32SysClock = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |SYSCTL_OSC_MAIN |SYSCTL_USE_PLL |SYSCTL_CFG_VCO_480), 60000000);	
	ui32SysClock = SysCtlClockFreqSet((SYSCTL_OSC_INT | SYSCTL_USE_PLL |SYSCTL_CFG_VCO_480), 20000000);
}

void S800_GPIO_Init(void)
{
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);						//Enable PortF
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));			//Wait for the GPIO moduleF ready
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);						//Enable PortJ	
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));			//Wait for the GPIO moduleJ ready	
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);						//Enable PortN	
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION)){};			//Wait for the GPIO moduleN ready		
	
  GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0);			//Set PF0 as Output pin
  GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0);			//Set PN0 as Output pin

	GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE,GPIO_PIN_0 | GPIO_PIN_1);//Set the PJ0,PJ1 as input pin
	GPIOPadConfigSet(GPIO_PORTJ_BASE,GPIO_PIN_0 | GPIO_PIN_1,GPIO_STRENGTH_2MA,GPIO_PIN_TYPE_STD_WPU);
}
	
void S800_I2C0_Init(void)
{
	
	
  SysCtlPeripheralEnable(SYSCTL_PERIPH_I2C0);
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
	GPIOPinConfigure(GPIO_PB2_I2C0SCL);
  GPIOPinConfigure(GPIO_PB3_I2C0SDA);
  GPIOPinTypeI2CSCL(GPIO_PORTB_BASE, GPIO_PIN_2);
  GPIOPinTypeI2C(GPIO_PORTB_BASE, GPIO_PIN_3);

	I2CMasterInitExpClk(I2C0_BASE,ui32SysClock, true);										//config I2C0 400k
	I2CMasterEnable(I2C0_BASE);	

	I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_CONFIG_PORT0,0x0ff);		//config port 0 as input
	I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_CONFIG_PORT1,0x0);			//config port 1 as output
	I2C0_WriteByte(TCA6424_I2CADDR,TCA6424_CONFIG_PORT2,0x0);			//config port 2 as output 

	I2C0_WriteByte(PCA9557_I2CADDR,PCA9557_CONFIG,0x00);					//config port as output
	I2C0_WriteByte(PCA9557_I2CADDR,PCA9557_OUTPUT,0x0ff);				//turn off the LED1-8
	
}

uint8_t I2C0_WriteByte(uint8_t DevAddr, uint8_t RegAddr, uint8_t WriteData)
{
	uint8_t rop;
	
	while(I2CMasterBusy(I2C0_BASE)){}; //æ�ȴ�
	I2CMasterSlaveAddrSet(I2C0_BASE, DevAddr, false); //��ӻ���ַ��д
	I2CMasterDataPut(I2C0_BASE, RegAddr);	//�����ݵ�ַ
	I2CMasterControl(I2C0_BASE, I2C_MASTER_CMD_BURST_SEND_START); //�������߷���
	while(I2CMasterBusy(I2C0_BASE)){};
	rop = (uint8_t)I2CMasterErr(I2C0_BASE);

	I2CMasterDataPut(I2C0_BASE, WriteData); //������ֵ
	I2CMasterControl(I2C0_BASE, I2C_MASTER_CMD_BURST_SEND_FINISH); //�������߷��ͣ����ͺ�ֹͣ
	while(I2CMasterBusy(I2C0_BASE)){};

	rop = (uint8_t)I2CMasterErr(I2C0_BASE);
	return rop;
}

uint8_t I2C0_ReadByte(uint8_t DevAddr, uint8_t RegAddr)
{
	uint8_t value;
	
	while(I2CMasterBusy(I2C0_BASE)){};	//æ�ȴ�
	I2CMasterSlaveAddrSet(I2C0_BASE, DevAddr, false); //��ӻ���ַ��д
	I2CMasterDataPut(I2C0_BASE, RegAddr); //�����ݵ�ַ
	I2CMasterControl(I2C0_BASE,I2C_MASTER_CMD_SINGLE_SEND); //�������߷���
	while(I2CMasterBusBusy(I2C0_BASE));
	I2CMasterErr(I2C0_BASE);
	Delay(1);
	//receive data
	I2CMasterSlaveAddrSet(I2C0_BASE, DevAddr, true); //��ӻ���ַ����
	I2CMasterControl(I2C0_BASE,I2C_MASTER_CMD_SINGLE_RECEIVE); //�������߽���
	while(I2CMasterBusBusy(I2C0_BASE));
	value=I2CMasterDataGet(I2C0_BASE);

	return value;
}

void S800_SysTick_Init(void)
{
	SysTickPeriodSet(ui32SysClock/SYSTICK_FREQUENCY); //��ʱ1ms
	SysTickEnable();
	SysTickIntEnable();
}

/*
	Corresponding to the startup_TM4C129.s vector table systick interrupt program name
*/
void SysTick_Handler(void)
{
	if (systick_100ms_couter == 0)
	{
		systick_100ms_couter = SYSTICK_FREQUENCY/10;
		systick_100ms_status = 1;
	}
	else
		systick_100ms_couter--;
	
	if (systick_10ms_couter	== 0)
	{
		systick_10ms_couter	 = SYSTICK_FREQUENCY/100;
		systick_10ms_status  = 1;
	}
	else
		systick_10ms_couter--;	
	
	if (GPIOPinRead(GPIO_PORTJ_BASE,GPIO_PIN_0) == 0)
	{
		systick_100ms_status	= systick_10ms_status = 0; 
		GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0,GPIO_PIN_0);		
	}
	else
		GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0,0);		
	
}

void Delay(uint32_t value)
{
	uint32_t ui32Loop;
	for(ui32Loop = 0; ui32Loop < value; ui32Loop++){};
}

