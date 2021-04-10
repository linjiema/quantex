// XMT_DLL_USB.h : XMT_DLL_USB DLL ����ͷ�ļ�
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
// �йش���ʵ�ֵ���Ϣ������� XMT_DLL_USB.cpp
//


// CXMT_DLL_USBApp
// �йش���ʵ�ֵ���Ϣ������� XMT_DLL_USB.cpp
//

//�ڲ�����ת����غ���
unsigned char* DataAnla_length_command(int f,unsigned char kk[2]); //������ת��Ϊ�ַ�����ȥ
unsigned char* DataAnla(float f,unsigned char kk[4]);
unsigned char *copy_arr_data(unsigned char target[],unsigned char source[],int num); //ת��������ڲ�������
unsigned char *copy_arr_data_float(unsigned char target[],unsigned char source[],int num); //����������ת����ȥ
void copy_arr_xmt_yll(unsigned char target[],unsigned char source[]);//����У��λ

//���͵�������
void SEND_V_COMMAND_SINGLE(libusb_device_handle *UsbHandle,int command_length,unsigned char a1,unsigned char b1,unsigned char c1,float data);


//�ڲ�������
unsigned char* DataAnla_Pro(double f,unsigned char kk[4]);
void receive_usb_info(int NumOfLibusbDevice,unsigned char receive_arr[]); //��ȡ��USB������ֵ

double XMT_ReDo_pro(unsigned char comand_Arr[]);
double Res_command_pro(unsigned char T_D_3,unsigned char T_D_4);//�������
float CalData(unsigned char kk0,unsigned char kk1,unsigned char kk2,unsigned char kk3);//����ת�� ������
unsigned char XMT_ReDo_pro_Unit(unsigned char comand_Arr[]); //������53��ȡ ��λ�� ��λ����
unsigned char Res_command_pro_Unit(unsigned char T_D_3,unsigned char T_D_4);//�������
void XMT_ReDo_PIDinfo(unsigned char tmpChannel ,unsigned char RecArr[],float PID[3]);//����PID
void XMT_ReadMultReal(  unsigned char comand_Arr[],
					  	unsigned char *OpenOrCloseFlag_0,
						double *Data_0,
						unsigned char *OpenOrCloseFlag_1,
						double *Data_1,
						unsigned char *OpenOrCloseFlag_2,
						double *Data_2
					);//���ɼ���������зְ�����

void XMT_ReDo_pro_Arr(unsigned char comand_Arr[],unsigned char arrRec[3]); //��ȡ����������ֵ��

//��������ת�� ������ת��ΪDA(0-65535)֮��ת��
void ChangeDataToDa(unsigned char TmpDa[2],float TmpSendData,float MaxData,float MinData); //�������� ת��Ϊ����[0] ������ֽ� �ȷ��� [1]������ֽں���

void XMT_ReadMultReal_Do( unsigned char T_D_3,unsigned char T_D_4,
									   	unsigned char *OpenOrCloseFlag_0,
										double *Data_0,
										unsigned char *OpenOrCloseFlag_1,
										double *Data_1,
										unsigned char *OpenOrCloseFlag_2,
							 			double *Data_2
										);
DLL_XMT_USB_API void DataAnla_ProLabviewDo(double f,unsigned char kk[4]);

extern "C"	DLL_XMT_USB_API int add(int x,int y);//��֤�򵥷���

DLL_XMT_USB_API int  print_devs_pro(libusb_device **devs);//�õ��м���usb��E17����E70���� ��������

extern "C"
{
	int DLL_XMT_USB_API SendABC(int UseUsbNum);
    DLL_XMT_USB_API int ScanUsbDevice(void);//ɨ�����ӵ�usb�豸 ����-1��ʾû���豸 ����0��ʾ����1���豸 ����1��ʾ���������豸 ͬʱ������usb�豸�ľ�����ظ�usb�豸���������
}


DLL_XMT_USB_API int TotalNumUsbDevice(void);//����usb�豸����
//��usb�豸��Ŵ�USB�豸
DLL_XMT_USB_API int OpenUsbNumOfDevice(libusb_device *dev, libusb_device_handle *handle);//�򿪰�˳���USB�豸
DLL_XMT_USB_API int OpenUsbNumOfDevice(int usbDeviceNum);//�򿪰�usb�豸��Ŵ�USB�豸,�����ʧ�ܣ���Ҫ�ٴ�ɨ������´򿪣�
DLL_XMT_USB_API int OpenUsbDeviceALL(int usbDeviceNum);//�м���usb�豸ȫ��һ���Դ򿪣�
DLL_XMT_USB_API int OpenUsbNumOfDeviceLabView(int usbDeviceNum);//�򿪰�usb�豸��Ŵ�USB�豸���߼�Щ
DLL_XMT_USB_API int CloseUsbNumOfDevice(int UsbNumOfDevice);//�رմ򿪵ĵ��豸


libusb_device_handle DLL_XMT_USB_API  *relibusb_device_handle(int tmpDataArrNum);//���� ����libusbDevice��Ӧ���
DLL_XMT_USB_API int print_devs_pro_ADD(libusb_device **devs,libusb_device *dev_rem_usb[20]);//�����洢���ӵ� �����ϵ�vid 0547 pid A516���������� //�������20̨usb �豸)//�õ��м���usb��E17����E70���� ��������

//����ͨ��usb�豸��������
DLL_XMT_USB_API int SendArrByusb(int UseUsbNum,unsigned char send_arr[],int ArrLong);
DLL_XMT_USB_API int SendArrByusb_Pro(libusb_device_handle *handle_TT,unsigned char send_arr[],int Arrlong);
DLL_XMT_USB_API  int  SendArrByusb_Pro_SEC(int UseUsbNum,unsigned char send_arr[],int Arrlong);

DLL_XMT_USB_API void RecArrFromUsb(int NumOfLibusbDevice,//�豸�ţ���0��ʼ
                                   unsigned char receive_arr[] //�ɼ������ݴ洢����
								   ); //��ȡ��USB������ֵ

extern "C"
{
  DLL_XMT_USB_API int OpenUsbPython(int usbusbDeviceNum);
}
extern "C"
{
//������  0 1  
DLL_XMT_USB_API void XMT_COMMAND_SinglePoint(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					double VoltOrMove_Data
					); //

//do ��·������ 2 3  
 DLL_XMT_USB_API   unsigned char XMT_COMMAND_MultSinglePoint(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					double VoltOrMove_Data_0,
					double VoltOrMove_Data_1,
					double VoltOrMove_Data_2
					);

//do�������� 4
DLL_XMT_USB_API void 	XMT_COMMAND_SinglePoint_Clear(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//�������� 5 6 
DLL_XMT_USB_API double XMT_COMMAND_ReadData(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//do ʵʱ���ݶ�ȡ�� 7 8 
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


//ֹͣ��ȡ 11
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_Stop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);
//������
//��·����  12 13 
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

//ֹͣ����  14 
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetHighSingleStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//��·��׼�ٶ�ģʽ 15 16 
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

//ֹͣ���� 17
DLL_XMT_USB_API void 	XMT_COMMAND_WaveSetMultWaveStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//����Э����
//����  18 20 22 
DLL_XMT_USB_API void 	XMT_COMMAND_Assist_SetFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					unsigned char SetFlag
					);

//��ȡflag���� 19 21 23 
DLL_XMT_USB_API unsigned char XMT_COMMAND_Assist_ReadFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num
					);

//�궨��������
//�趨ϵͳ��  24 26 28 
DLL_XMT_USB_API void 	XMT_COMMAND_SetSystemInfo(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					double SystemInfo
					);

//�������� 25 27  29
DLL_XMT_USB_API double XMT_COMMAND_ReadSystemInfo(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num
					);

//�趨�ߵ���
//30 32 34
DLL_XMT_USB_API void 	XMT_COMMAND_SetSystemHL_Limit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					double SystemInfo
					);

//��ȡϵͳ�ߵ��� 31 33 35 
double DLL_XMT_USB_API  XMT_COMMAND_ReadSystemHL_Limit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num					
					);


// 36 ����PID ����/ֹͣ 
DLL_XMT_USB_API void 	XMT_COMMAND_SETPID_RorH(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,
					unsigned char PIDSetFlag
					); //���� 'R' ֹͣ 'H' 20170829

//37 ����PID����
DLL_XMT_USB_API void SendArray_PID_Channel(  int usbDeviceNum,
	                     int address,//��ַ��
						 int Command_B3,//ָ����
						 int Command_B4,//ָ����
						 unsigned char Channel_Num,
						 float PID_P,
						 float PID_I,
						 float PID_D
						 );//�������� 20170829
//38 ��ȡ PID ���� 
DLL_XMT_USB_API void Read_PID_Channel(  int usbDeviceNum,
	                     int address,//��ַ��
						 int Command_B3,//ָ����
						 int Command_B4,//ָ����
						 unsigned char Channel_Num,
						 float PID_Rc[3]
						 ); 
//39 40 41 42 43 44 45 ����ʹ��
///////////////////////////////

//46 �趨��λ����ַ �������ظ�����10��
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCUAddress(int usbDeviceNum,
	                unsigned char address,//0x00 ����ǹ㲥��ַ �̶���
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char SetAddress////Ԥ���ַ
					);
//47 ��ȥ��λ����ַ
DLL_XMT_USB_API unsigned char 	XMT_COMMAND_ReadMCUAddress(int usbDeviceNum,
	                unsigned char address,//0x00 ����ǹ㲥��ַ �̶���
					unsigned char Command_B3,
					unsigned char Command_B4
					);

//��ȡϵͳ�� 48 
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS_UpDoPro(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char TimerSet_ms,
					unsigned char Flag_Channe_OpenOrClose
					);


//��ȡϵͳ�� 49
DLL_XMT_USB_API void 	XMT_COMMAND_ReadData_TS_DownDoPro(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char TimerSet_ms
					);

// 50 ����У��
DLL_XMT_USB_API void XMT_COMMAND_CONTROL_PID(         int usbDeviceNum,
	                                  int address_ma,//��ַ��
									  int bao_long,  //����
									  int zhilingma_B3,//ָ����
									  int zhilingma_B4,//ָ����
									  unsigned char channel_num,//ͨ����
									  unsigned char FLAG_CLoseOrOpen//��ʼ����
							);

//51  ��ȡ��·λ�ƻ��ѹ���� [5]��ѹ/λ��bit��־ [1111] ����ͬͨ���Ŀ��ջ�����ֵ 3 2 1 0 ͨ����Ӧ
DLL_XMT_USB_API void 	XMT_COMMAND_ReadMultChannelMoveOrVolt(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char *OpenOrCloseFlag_0,//���ջ����� 
					double *Data_0,//���ص�����ֵ
					unsigned char *OpenOrCloseFlag_1,//���ջ�����
					double *Data_1,//���ص�����ֵ
					unsigned char *OpenOrCloseFlag_2,//���ջ�����
					double *Data_2//���ص�����ֵ
					);

//52 ��ȡ��ѹλ�����ưٷֱ�
DLL_XMT_USB_API float 	XMT_COMMAND_ReadSystem_VoltPer(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
				); 


//53 ��ȡ��λ����λ
DLL_XMT_USB_API unsigned char 	XMT_COMMAND_ReadSystem_Unit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
				); 

//54 ��ȡĳһ·��������ֹͣ�ٶ�
DLL_XMT_USB_API unsigned char  XMT_COMMAND_ReadWaveBeginAndStopSpeed(int usbDeviceNum,
	                int address_ma,//��ַ��
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char channel_num // ͨ���� 0 1 2 
					);// 'H'�������  'L'������� 


//55��λ������ĳһ·��������ֹͣ�ٶȣ�����ֹͣ�ٶ�һ�£�
DLL_XMT_USB_API void XMT_COMMAND_SetWaveBeginAndStopSpeed(int usbDeviceNum,
	                int address_ma,//��ַ��
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char channel_num, // ͨ���� 0 1 2 
					unsigned char WaveBeginAndStopFlag // 'H'�������  'L'������� 
					);

//56 ��λ��������λ����λ
DLL_XMT_USB_API void XMT_COMMAND_SetMCUMardOrUm(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char MCUMardOrUm //0 �Ƕ� 1 λ��
	          );
//57 ��λ��������λ����λ
DLL_XMT_USB_API void XMT_COMMAND_SetMCUE09orOther(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char MCUDoFlag //0 E709 1 E517
	          );
//58 �趨��λ����ѹλ�����ưٷֱ�
DLL_XMT_USB_API void XMT_COMMAND_SetMCUVoltOrUmPP(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					float tmpData //0��1 ��С��
	          );
			  
// 59 60 //����У�� �Լ�PID������״̬
DLL_XMT_USB_API  void  XMT_COMMAND_ReadMCU_PIDFlag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char ChannelFlag[3]//'Y'��Ч 'N'��ʾ��Ч  ��������ֵ
					);
// 61 62 �ڶ�̨���� ����422������ʱ��ʹ��

// 63 
//ͨ��usbͨ�Ŷ˿�������λ������ͨ�Ų�����
DLL_XMT_USB_API void  XMT_COMMAND_SetMCUComBit(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char ComBitFlag
					);
/* //������λ��������
  ��A��9600 ��B��19200  ��C��38400 ��D��57600    
  ��E��76800��F��115200 ��G��128000��H��230400 
  ��I��256000 
   //20170509
*/

// 64  AVRר�ÿ���jtag
DLL_XMT_USB_API void  XMT_COMMAND_SetMCUJtag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char AVRFlag //[5]����AVR Jtag���� ��S��
					);


//65 �����������ת���ɼ�����
DLL_XMT_USB_API void XMT_COMMAND_LetMCUToReadData(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4
					);


//��λ��ģʽ��� 66 67 
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

//[5]ͨ����
//[6]��S��������ǰ·���� ��T��ֹͣ��ǰ·����
DLL_XMT_USB_API void XMT_COMMAND_XWJ_ChannelDoOrStop(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channel_Num,// 0 1 2 
                    unsigned char FlagMult //��S��������ǰ·���� ��T��ֹͣ��ǰ·����
					);


//Mult���� 69 ��S����·ͬ������ 'T'��·ͬʱֹͣ
DLL_XMT_USB_API unsigned char XMT_COMMAND_Assist_Flag(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char FlagMult
					);


//70 ���㲽���洢
DLL_XMT_USB_API unsigned char XMT_COMMAND_SaveDataArrToMCU(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channle_flag,
                    unsigned char Flag_AheadOrLeg,//0��ʾǰ48�� 1��ʾ��48��
					float ArrData[],
					unsigned char LongArrData,//���͵����ݵ���0��48,
					float MaxData,//�������ֵ ������� һ��Ϊ150��120
					float MinData//��С����ֵ ����ʵ����Ҫ��������
					);

//70_PPPP ���㲽���洢
//70_PPPP ���㲽���洢
DLL_XMT_USB_API unsigned char XMT_COMMAND_SaveDataArrToMCU_TEST(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					unsigned char Channle_flag,
                    unsigned char Flag_AheadOrLeg,//0��ʾǰ48�� 1��ʾ��48��
					float ArrData[3],
					unsigned char LongArrData,//���͵����ݵ���0��48,
					float MaxData,//�������ֵ ������� һ��Ϊ150��120
					float MinData,//��С����ֵ ����ʵ����Ҫ��������
					unsigned char ReArr[18]
					);

//70_PPPP_WWWW ���㲽���洢
DLL_XMT_USB_API float XMT_COMMAND_ArrAdd(float a[3]);
					//70_PPPP ���㲽���洢

					//70_PPPP ���㲽���洢
DLL_XMT_USB_API float XMT_COMMAND_SaveDataArrToMCU_TEST_AAA(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
					float ArrData[3],
					unsigned char LongArrData,//���͵����ݵ���0��48,
					unsigned char *ReArr
					);



//71 �趨����ʱ��
//�趨��λ���͵����ʱ��
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCUSendDataTimer(int usbDeviceNum,
	                unsigned char address,
					unsigned char Command_B3,
					unsigned char Command_B4,
                    unsigned char Channel_Num,
					float SendDataTimer//0.1����-9999����֮��
					);


// 72 ����Ԥ���趨�õĳ��� ����/ֹͣ 
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_BeginSend(int usbDeviceNum,// 0 , 1 , 2 
	                unsigned char address,
					unsigned char Command_B3,//36
					unsigned char Command_B4,//0
					unsigned char Channel_Num,//0,1,2
					unsigned char RunFlag//'S'��ʼ    'T' ֹͣ   'P'��ͣ 
					);


// 73 �趨DA���ֵ���Ŵ����
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagDa(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								unsigned char DaFlag,//'Z' �趨Ϊ0����� 'M'�趨���ֵ���� 
								float FlagForDa//[7][8][9][10] ������ֵ������
					);

// 74 �趨����DA��ʼֵ
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagVolt(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								float FlagForVolt//[6][7][8][9] DA�����ѹ�ٷֱ� DA��ʼֵ���ֵ�ٷֱ�Ϊ0-1С����0�������0��1�����������ѹֵ
					);

// 75 AD�ɼ�������Ŵ�
DLL_XMT_USB_API void 	XMT_COMMAND_SetMCU_FlagAD(int usbDeviceNum,// 0 , 1 , 2 
	                            unsigned char address,
								unsigned char Command_B3,//36
								unsigned char Command_B4,//0
								unsigned char Channel_Num,//0,1,2
								unsigned char FlagAD,//[6]'Z'��ʼ���� 'M'��ʼ���Ŵ�
								unsigned char FlagCloseOrOpen //[7]'C'�ջ� 'O'����
					);
}
void DLL_XMT_USB_API SendABC_P(int UseUsbNum,int address);//���������ת���ɼ�����

DLL_XMT_USB_API void dis_Num100us(int tmpUs_100us);//100us�������� 
DLL_XMT_USB_API void ArrDataSend(int usbDeviceNum,unsigned char address,unsigned char Channel_Num,double arr[],int ArrLong,unsigned char flagOpenOrClose,int tmpUs_100us);
DLL_XMT_USB_API void ArrDataSendAToB(int usbDeviceNum,unsigned char address,unsigned char Channel_Num,unsigned char flagOpenOrClose,double Point_A,double Point_B,int ArrLong,int tmpUs_100us);

DLL_XMT_USB_API void StopAtoB(int tmpSend);
	//�������� �Լ����鳤�� flagOpenOrClose���ջ� �趨 'C'��ʾ�ջ� 'O'��ʾ����,���ͼ��100΢��������
//{�� flagOpenOrClose���ջ� �趨 'C'��ʾ�ջ� 'O'��ʾ����,���ͼ��100΢��������

#endif 