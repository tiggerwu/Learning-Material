
#include <stdio.h>
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
#include "systick.h"
#include "interrupt.h"
#include "uart.h"
#include "string.h"
#include "hw_ints.h"


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




void 		S800_GPIO_Init(void);
void		S800_I2C0_Init(void);
void 		S800_UART_Init(void);
void UARTStringPut( char *PutMessage);
void show(int,int);
uint8_t 	I2C0_WriteByte(uint8_t DevAddr, uint8_t RegAddr, uint8_t WriteData);
uint32_t ui32SysClock;
char Stringget[13],Stringput[13],disp_buff[9];
uint8_t hour=12, minute=56, second=3;
volatile uint8_t i=0;
int count;
bool flag=0;

//the disp_tab and disp_tab_7seg must be the Corresponding relation
//the last character should be the space(not display) character
char	const disp_tab[]			={'0','1','2','3','4','5',     //the could display char and its segment code   
															 '6','7','8','9','A','b',
															 'C','d','E','F',
															 'H','L','P','o',
															 '.','-','_',' '}; 
char const disp_tab_7seg[]	={0x3F,0x06,0x5B,0x4F,0x66,0x6D,  
															0x7D,0x07,0x7F,0x6F,0x77,0x7C,
															0x39,0x5E,0x79,0x71, 
															0x76,0x38,0x73,0x5c,
															0x80,0x40, 0x08,0x00}; 

int min=0, min1=0, min2=0, sec=0, sec1=0, sec2=0;
															
int main(void)
{
	//use internal 16M oscillator, PIOSC
 		
	ui32SysClock = SysCtlClockFreqSet((SYSCTL_OSC_INT | SYSCTL_USE_OSC), 16000000);
	
  SysTickPeriodSet(ui32SysClock);
	SysTickEnable();
	SysTickIntEnable();
	
	S800_GPIO_Init();
	S800_I2C0_Init();
	S800_UART_Init();
	
	IntEnable(INT_UART0);
	UARTIntEnable(UART0_BASE, UART_INT_RX | UART_INT_RT);	//Enable UART0 RX,TX interrupt
  IntMasterEnable();		

	
	
	while (1)
	{
		flag=0;
		
		if(Stringget[0]!=0)
		{
			min1=(Stringget[0]-'0')*10+Stringget[1]-'0';
			min2=(Stringget[6]-'0')*10+Stringget[7]-'0';
			sec1=(Stringget[3]-'0')*10+Stringget[4]-'0';
			sec2=(Stringget[9]-'0')*10+Stringget[10]-'0';
			flag=1;				

		}
		
		if(flag)
		{
			switch(Stringget[5])
			{
				case '+':min=min1+min2;sec=sec1+sec2;break;
				default:min=min1-min2;sec=sec1-sec2;break;
			}
			
			memset(Stringget, 0, sizeof(Stringget));
			
			if(sec>=60)
			{
				sec-=60;
				min++;
			}
			if(sec<0)
			{
				sec+=60;
				min--;
			}
			if(min>=60)min-=60;
			if(min<0)min+=60;
			
			show(min,sec);
		}

	}

}


void UARTStringPut( char *PutMessage)
{
	while(*PutMessage!='\0')
		UARTCharPut(UART0_BASE,*(PutMessage++));
}

void show(int min,int sec)
{
	sprintf(Stringput,"%02u%s%02u",min,":",sec);
	UARTStringPut(Stringput);
	memset(Stringput, 0, sizeof(Stringput));
}

void S800_UART_Init(void)
{
	SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);						//Enable PortA
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));			//Wait for the GPIO moduleA ready

	GPIOPinConfigure(GPIO_PA0_U0RX);												// Set GPIO A0 and A1 as UART pins.
  GPIOPinConfigure(GPIO_PA1_U0TX);    			

  GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);

	// Configure the UART for 115,200, 8-N-1 operation.
  UARTConfigSetExpClk(UART0_BASE, ui32SysClock,115200,(UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE |UART_CONFIG_PAR_NONE));
	UARTStringPut("\r\nHello, world!\r\n");
	UARTFIFOLevelSet(UART0_BASE, UART_FIFO_TX1_8, UART_FIFO_RX7_8);
}
void S800_GPIO_Init(void)
{
	SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);						//Enable PortF
	while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF)){};			//Wait for the GPIO moduleF ready
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
	while(I2CMasterBusy(I2C0_BASE)){};
	I2CMasterSlaveAddrSet(I2C0_BASE, DevAddr, false);
	I2CMasterDataPut(I2C0_BASE, RegAddr);
	I2CMasterControl(I2C0_BASE, I2C_MASTER_CMD_BURST_SEND_START);
	while(I2CMasterBusy(I2C0_BASE)){};
	rop = (uint8_t)I2CMasterErr(I2C0_BASE);

	I2CMasterDataPut(I2C0_BASE, WriteData);
	I2CMasterControl(I2C0_BASE, I2C_MASTER_CMD_BURST_SEND_FINISH);
	while(I2CMasterBusy(I2C0_BASE)){};

	rop = (uint8_t)I2CMasterErr(I2C0_BASE);
	return rop;
}

/*
	Corresponding to the startup_TM4C129.s vector table systick interrupt program name
*/
void SysTick_Handler(void)
{
	
}

void UART0_Handler(void)
{
//  没有必要手段清除中断，原因是当从FIFO中读取字符时，会自动清除中断
//  int32_t uart0_int_status;
// uart0_int_status 		= UARTIntStatus(UART0_BASE, true);		// Get the interrrupt status.

//UARTIntClear(UART0_BASE, uart0_int_status);					//Clear the asserted interrupts
	
	
	while(UARTCharsAvail(UART0_BASE))
	{
			Stringget[i]=UARTCharGet(UART0_BASE);
			i++;
	}
		Stringget[i]='\0';
		i=0;	
 }
