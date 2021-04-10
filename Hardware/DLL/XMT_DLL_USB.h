// XMT_DLL_USB.h : XMT_DLL_USB DLL 的主头文件
//
//xmt
#include "libusb.h"
#ifdef DLL_XMT_USB_EXPORTS
#define DLL_XMT_USB_API __declspec(dllexport)
#else
#define DLL_XMT_USB_API __declspec(dllexport)
#endif


#ifndef _DATA_H_ 
#define _DATA_H_ 
//

// CXMT_DLL_USBApp
// 有关此类实现的信息，请参阅 XMT_DLL_USB.cpp
//


// CXMT_DLL_USBApp
// 有关此类实现的信息，请参阅 XMT_DLL_USB.cpp
//

//内部数据转换相关函数
unsigned char* DataAnla_length_command(int f,unsigned char kk[2]); //将长度转化为字符发下去
unsigned char* DataAnla(float f,unsigned char kk[4]);
unsigned char *copy_arr_data(unsigned char target[],unsigned char source[],int num); //转移数组的内部的数据
unsigned char *copy_arr_data_float(unsigned char target[],unsigned char source[],int num); //将浮点数据转换过去
void copy_arr_xmt_yll(unsigned char target[],unsigned char source[]);//拷贝校验位

//发送单点命令
void SEND_V_COMMAND_SINGLE(libusb_device_handle *UsbHandle,int command_length,unsigned char a1,unsigned char b1,unsigned char c1,float data);


//内部处理函数
unsigned char* DataAnla_Pro(double f,unsigned char kk[4]);
void receive_usb_info(int NumOfLibusbDevice,unsigned char receive_arr[]); //读取的USB的数据值

double XMT_ReDo_pro(unsigned char comand_Arr[]);
double Res_command_pro(unsigned char T_D_3,unsigned char T_D_4);//解包命令
float CalData(unsigned char kk0,unsigned char kk1,unsigned char kk2,unsigned char kk3);//用来转化 正负数
unsigned char XMT_ReDo_pro_Unit(unsigned char comand_Arr[]); //用于做53读取 下位机 单位数据
unsigned char Res_command_pro_Unit(unsigned char T_D_3,unsigned char T_D_4);//解包命令
void XMT_ReDo_PIDinfo(unsigned char tmpChannel ,unsigned char RecArr[],float PID[3]);//解码PID
void XMT_ReadMultReal(  unsigned char comand_Arr[],
					  	unsigned char *OpenOrCloseFlag_0,
						double *Data_0,
						unsigned char *OpenOrCloseFlag_1,
						double *Data_1,
						unsigned char *OpenOrCloseFlag_2,
						double *Data_2
					);//将采集的数组进行分包处理

void XMT_ReDo_pro_Arr(unsigned char comand_Arr[],unsigned char arrRec[3]); //读取带返回数据值得

//发送数据转换 浮点数转化为DA(0-65535)之间转换
void ChangeDataToDa(unsigned char TmpDa[2],float TmpSendData,float MaxData,float MinData); //将浮点数 转化为两个[0] 代表高字节 先发送 [1]代表低字节后发送

void XMT_ReadMultReal_Do( unsigned char T_D_3,unsigned char T_D_4,
									   	unsigned char *OpenOrCloseFlag_0,
										double *Data_0,
										unsigned char *OpenOrCloseFlag_1,
										double *Data_1,
										unsigned char *OpenOrCloseFlag_2,
							 			double *Data_2
										);
DLL_XMT_USB_API void DataAnla_ProLabviewDo(double f,unsigned char kk[4]);

extern "C"	DLL_XMT_USB_API int add(int x,int y);//验证简单方法

DLL_XMT_USB_API int  print_devs_pro(libusb_device **devs);//得到有几个usb的E17或是E70连接 首先运行

extern "C"
{
	int DLL_XMT_USB_API SendABC(int UseUsbNum);
    DLL_XMT_USB_API int ScanUsbDevice(void);//扫描连接的usb设备 返回-1表示没有设备 返回0表示连接1个设备 返回1表示连接两个设备 同时将连接usb设备的句柄返回给usb设备句柄的数组
}


DLL_XMT_USB_API int TotalNumUsbDevice(void);//返回usb设备总数
//按usb设备编号打开USB设备
DLL_XMT_USB_API int OpenUsbNumOfDevice(libusb_device *dev, libusb_device_handle *handle);//打开按顺序的USB设备
DLL_XMT_USB_API int OpenUsbNumOfDevice(int usbDeviceNum);//打开按usb设备编号打开USB设备,如果打开失败，需要再次扫描后重新打开！
DLL_XMT_USB_API int OpenUsbDeviceALL(int usbDeviceNum);//有几个usb设备全部一次性打开！
DLL_XMT_USB_API int OpenUsbNumOfDeviceLabView(int usbDeviceNum);//打开按usb设备编号打开USB设备更高级些
DLL_XMT_USB_API int CloseUsbNumOfDevice(int UsbNumOfDevice);//关闭打开的的设备


libusb_device_handle DLL_XMT_USB_API  *relibusb_device_handle(int tmpDataArrNum);//返回 生成libusbDevice对应句柄
DLL_XMT_USB_API int print_devs_pro_ADD(libusb_device **devs,libusb_device *dev_rem_usb[20]);//用来存储连接到 电脑上的vid 0547 pid A516这两个数据 //最多连接20台usb 设备)//得到有几个usb的E17或是E70连接 首先运行

//发送通过usb设备发送数据
DLL_XMT_USB_API int SendArrByusb(int UseUsbNum,unsigned char send_arr[],int ArrLong);
DLL_XMT_USB_API int SendArrByusb_Pro(libusb_device_handle *handle_TT,unsigned char send_arr[],int Arrlong);
DLL_XMT_USB_API  int  SendArrByusb_Pro_SEC(int UseUsbNum,unsigned char send_arr[],int Arrlong);

DLL_XMT_USB_API void RecArrFromUsb(int NumOfLibusbDevice,//设备号，从0开始
                                   unsigned char receive_arr[] //采集的数据存储数组
								   ); //读取的USB的数据值

extern "C"
{
  DLL_XMT_USB_API int OpenUsbPython(int usbusbDeviceNum);
}
extern "C"
{
//单点类  0 1  
DLL_XMT_USB_API void XMT_COMMAND_SinglePoint(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					double VoltOrMove_Data
					); //

//do 多路单点类 2 3  
 DLL_XMT_USB_API   unsigned char XMT_COMMAND_MultSinglePoint(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					double VoltOrMove_Data_0,
					double VoltOrMove_Data_1,
					double VoltOrMove_Data_2
					);

//do清零命令 4
DLL_XMT_USB_API void 	XMT_COMMAND_SinglePoint_Clear(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//读数据类 5 6 
DLL_XMT_USB_API double XMT_COMMAND_ReadData(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//do 实时数据读取类 7 8 
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char TimerSet_ms
					);

// 9 10 
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS_MultChannle(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char TimerSet_ms
					);


//停止读取 11
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_Stop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);
//波形类
//单路高速  12 13 
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetHighSingle(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char WaveType,
					double FengFengZhi,
					double PinLvHz,
					double Pianzhi
					);

//停止发送  14 
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetHighSingleStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//多路标准速度模式 15 16 
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetMultWave(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char WaveType,
					double FengFengZhi,
					double PinLvHz,
					double Pianzhi
					);

//停止发送 17
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetMultWaveStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//辅助协助类
//设置  18 20 22 
DLL_XMT_USB_API void 	XMT_COMMAND_Assist_SetFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					unsigned char SetFlag
					);

//读取flag数据 19 21 23 
DLL_XMT_USB_API unsigned char XMT_COMMAND_Assist_ReadFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num
					);

//标定和配置类
//设定系统类  24 26 28 
DLL_XMT_USB_API void 	XMT_COMMAND_SetSystemInfo(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					double SystemInfo
					);

//读数据类 25 27  29
DLL_XMT_USB_API double XMT_COMMAND_ReadSystemInfo(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//设定高低限
//30 32 34
DLL_XMT_USB_API void 	XMT_COMMAND_SetSystemHL_Limit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					double SystemInfo
					);

//读取系统高低限 31 33 35 
double DLL_XMT_USB_API  XMT_COMMAND_ReadSystemHL_Limit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num					
					);


// 36 设置PID 启动/停止 
DLL_XMT_USB_API void 	XMT_COMMAND_SETPID_RorH(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char PIDSetFlag
					); //启动 'R' 停止 'H' 20170829

//37 设置PID参数
DLL_XMT_USB_API void SendArray_PID_Channel(  int usbDeviceNum,
	                     int address,//地址码
						 int Command_B3,//指令码
						 int Command_B4,//指令码
						 unsigned char Channel_Num,
						 float PID_P,
						 float PID_I,
						 float PID_D
						 );//发送数据 20170829
//38 读取 PID 参数 
DLL_XMT_USB_API void Read_PID_Channel(  int usbDeviceNum,
	                     int address,//地址码
						 int Command_B3,//指令码
						 int Command_B4,//指令码
						 unsigned char Channel_Num,
						 float PID_Rc[3]
						 ); 
//39 40 41 42 43 44 45 特殊使用
///////////////////////////////

//46 设定下位机地址 该命令重复发送10次
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCUAddress(int usbDeviceNum,
	                unsigned char address,//0x00 这个是广播地址 固定的
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char SetAddress////预设地址
					);
//47 读去下位机地址
DLL_XMT_USB_API unsigned char 	XMT_COMMAND_ReadMCUAddress(int usbDeviceNum,
	                unsigned char address,//0x00 这个是广播地址 固定的
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//读取系统类 48 
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS_UpDoPro(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char TimerSet_ms,
					unsigned char Flag_Channe_OpenOrClose
					);


//读取系统类 49
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS_DownDoPro(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char TimerSet_ms
					);

// 50 幅度校正
DLL_XMT_USB_API void XMT_COMMAND_CONTROL_PID(         int usbDeviceNum,
	                                  int address_ma,//地址码
									  int bao_long,  //包长
									  int zhilingma_B3,//指令码
									  int zhilingma_B4,//指令码
									  unsigned char channel_num,//通道数
									  unsigned char FLAG_CLoseOrOpen//开始结束
							);

//51  读取多路位移或电压数据 [5]电压/位移bit标志 [1111] 代表不同通道的开闭环数据值 3 2 1 0 通道对应
DLL_XMT_USB_API void 	XMT_COMMAND_ReadMultChannelMoveOrVolt(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char *OpenOrCloseFlag_0,//开闭环数据 
					double *Data_0,//返回的数据值
					unsigned char *OpenOrCloseFlag_1,//开闭环数据
					double *Data_1,//返回的数据值
					unsigned char *OpenOrCloseFlag_2,//开闭环数据
					double *Data_2//返回的数据值
					);

//52 读取电压位移限制百分比
DLL_XMT_USB_API float 	XMT_COMMAND_ReadSystem_VoltPer(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
				); 


//53 读取下位机单位
DLL_XMT_USB_API unsigned char 	XMT_COMMAND_ReadSystem_Unit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
				); 

//54 读取某一路波形启动停止速度
DLL_XMT_USB_API unsigned char  XMT_COMMAND_ReadWaveBeginAndStopSpeed(int usbDeviceNum,
	                int address_ma,//地址码
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char channel_num // 通道数 0 1 2 
					);// 'H'代表高速  'L'代表低速 


//55上位机设置某一路波形启动停止速度（启动停止速度一致）
DLL_XMT_USB_API void XMT_COMMAND_SetWaveBeginAndStopSpeed(int usbDeviceNum,
	                int address_ma,//地址码
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char channel_num, // 通道数 0 1 2 
					unsigned char WaveBeginAndStopFlag // 'H'代表高速  'L'代表低速 
					);

//56 上位机设置下位机单位
DLL_XMT_USB_API void XMT_COMMAND_SetMCUMardOrUm(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char MCUMardOrUm //0 角度 1 位移
	          );
//57 上位机设置下位机单位
DLL_XMT_USB_API void XMT_COMMAND_SetMCUE09orOther(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char MCUDoFlag //0 E709 1 E517
	          );
//58 设定下位机电压位移限制百分比
DLL_XMT_USB_API void XMT_COMMAND_SetMCUVoltOrUmPP(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					float tmpData //0到1 的小数
	          );
			  
// 59 60 //幅度校正 以及PID的数字状态
DLL_XMT_USB_API  void  XMT_COMMAND_ReadMCU_PIDFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char ChannelFlag[3]//'Y'有效 'N'表示无效  返回数据值
					);
// 61 62 在多台机器 串口422相连接时候使用

// 63 
//通过usb通信端口设置下位机串口通信波特率
DLL_XMT_USB_API void  XMT_COMMAND_SetMCUComBit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char ComBitFlag
					);
/* //设置下位机波特率
  ‘A’9600 ‘B’19200  ‘C’38400 ‘D’57600    
  ‘E’76800‘F’115200 ‘G’128000‘H’230400 
  ‘I’256000 
   //20170509
*/

// 64  AVR专用开启jtag
DLL_XMT_USB_API void  XMT_COMMAND_SetMCUJtag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char AVRFlag //[5]开启AVR Jtag功能 ‘S’
					);


//65 从任意界面跳转到采集界面
DLL_XMT_USB_API void XMT_COMMAND_LetMCUToReadData(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);


//相位角模式输出 66 67 
DLL_XMT_USB_API void XMT_COMMAND_WaveSetMultWaveXwj(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char  WaveType,
					double FengFengZhi,
					double PinLvHz,
					double Pianzhi,
					double Xwjiao
					);

//[5]通道数
//[6]‘S’启动当前路波形 ‘T’停止当前路波形
DLL_XMT_USB_API void XMT_COMMAND_XWJ_ChannelDoOrStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,// 0 1 2 
                    unsigned char FlagMult //‘S’启动当前路波形 ‘T’停止当前路波形
					);


//Mult数据 69 ‘S’三路同步启动 'T'三路同时停止
DLL_XMT_USB_API unsigned char XMT_COMMAND_Assist_Flag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char FlagMult
					);


//70 单点步进存储
DLL_XMT_USB_API unsigned char XMT_COMMAND_SaveDataArrToMCU(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channle_flag,
                    unsigned char Flag_AheadOrLeg,//0表示前48点 1表示后48点
					float ArrData[],
					unsigned char LongArrData,//发送的数据点数0到48,
					float MaxData,//最大数据值 如果开环 一般为150或120
					float MinData//最小数据值 根据实际需要来做决定
					);

//70_PPPP 单点步进存储
//70_PPPP 单点步进存储
DLL_XMT_USB_API unsigned char XMT_COMMAND_SaveDataArrToMCU_TEST(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channle_flag,
                    unsigned char Flag_AheadOrLeg,//0表示前48点 1表示后48点
					float ArrData[3],
					unsigned char LongArrData,//发送的数据点数0到48,
					float MaxData,//最大数据值 如果开环 一般为150或120
					float MinData,//最小数据值 根据实际需要来做决定
					unsigned char ReArr[18]
					);

//70_PPPP_WWWW 单点步进存储
DLL_XMT_USB_API float XMT_COMMAND_ArrAdd(float a[3]);
					//70_PPPP 单点步进存储

					//70_PPPP 单点步进存储
DLL_XMT_USB_API float XMT_COMMAND_SaveDataArrToMCU_TEST_AAA(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					float ArrData[3],
					unsigned char LongArrData,//发送的数据点数0到48,
					unsigned char *ReArr
					);



//71 设定发送时间
//设定下位发送单点的时间
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCUSendDataTimer(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					float SendDataTimer//0.1毫秒-9999毫秒之间
					);


// 72 发送预先设定好的程序 启动/停止 
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_BeginSend(int usbDeviceNum,// 0 , 1 , 2 
	                unsigned char address,
					unsigned char Command_B3,//36
					unsigned char Command_B4,//0
					unsigned char Channel_Num,//0,1,2
					unsigned char RunFlag//'S'开始    'T' 停止   'P'暂停 
					);


// 73 设定DA数字调零放大参数
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagDa(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								unsigned char DaFlag,//'Z' 设定为0点参数 'M'设定最大值参数 
								float FlagForDa//[7][8][9][10] 参数数值浮点数
					);

// 74 设定开机DA初始值
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagVolt(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								float FlagForVolt//[6][7][8][9] DA输出电压百分比 DA初始值最大值百分比为0-1小数，0代表输出0，1代表输出最大电压值
					);

// 75 AD采集调零调放大
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagAD(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								unsigned char FlagAD,//[6]'Z'开始调零 'M'开始调放大
								unsigned char FlagCloseOrOpen //[7]'C'闭环 'O'开环
					);
}
void DLL_XMT_USB_API SendABC_P(int UseUsbNum,int address);//任意界面跳转到采集界面

DLL_XMT_USB_API void dis_Num100us(int tmpUs_100us);//100us的整数倍 
DLL_XMT_USB_API void ArrDataSend(int usbDeviceNum,unsigned char address,unsigned char Channel_Num,double arr[],int ArrLong,unsigned char flagOpenOrClose,int tmpUs_100us);
DLL_XMT_USB_API void ArrDataSendAToB(int usbDeviceNum,unsigned char address,unsigned char Channel_Num,unsigned char flagOpenOrClose,double Point_A,double Point_B,int ArrLong,int tmpUs_100us);

DLL_XMT_USB_API void StopAtoB(int tmpSend);
	//发送数组 以及数组长度 flagOpenOrClose开闭环 设定 'C'表示闭环 'O'表示开环,发送间隔100微秒整数倍
//{度 flagOpenOrClose开闭环 设定 'C'表示闭环 'O'表示开环,发送间隔100微秒整数倍

#endif 