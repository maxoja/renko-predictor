#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   1
#property indicator_type1   DRAW_COLOR_LINE
#property indicator_color1  clrWhite,clrGreen,clrRed
#property indicator_width1  2
//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
input int InpBoxSizePoint = 100;
input bool InpProduceSequence = false;
input string InpFileName = "default.txt";

double lineBuffer[];
double colorBuffer[];
double boxSize;

int OnInit()
  {
//--- indicator buffers mapping
   if (InpBoxSizePoint >= 50)
      boxSize = InpBoxSizePoint * Point();
   else
      boxSize = 50 * Point();
      
//--- indicator buffers mapping
   SetIndexBuffer(0, lineBuffer, INDICATOR_DATA);
   SetIndexBuffer(1, colorBuffer, INDICATOR_COLOR_INDEX);
//---
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
//---
   IndicatorSetString(INDICATOR_SHORTNAME, "My Renko ("+InpBoxSizePoint+" Points)");   
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
  {
//---
   const int rightMost = rates_total-1;
   const int leftMost = 0;
   const int shiftPrev = -1;
   const int shiftNext = 1;
   
   for(int i = leftMost; i <= rightMost && !IsStopped(); i += shiftNext) {
      if(i == 0) {
         // first left-most bar
         lineBuffer[i] = nearestSteppedPrice(price[i]);
         colorBuffer[i] = 0;
         continue;
      }
         
         double pivot = lineBuffer[i+shiftPrev];
         double distance = price[i] - pivot;
         int step = distanceToStep(distance);
         
         if(step == 0) {
            lineBuffer[i] = lineBuffer[i+shiftPrev];
            colorBuffer[i] = colorBuffer[i+shiftPrev];
            continue;
         }
         
         lineBuffer[i] = pivot + step*boxSize;
         
         if(step > 0)
            colorBuffer[i] = 1;
         else
            colorBuffer[i] = 2;
         
      }

//--- return value of prev_calculated for next call
   return(rates_total);
  }
//+------------------------------------------------------------------+

double nearestSteppedPrice(double price) {
   int temp = (price+boxSize*0.5) / boxSize;
   return temp * boxSize;
}

int distanceToStep(double distance) {
   if(MathAbs(distance) < boxSize)
      return 0;
   return distance/boxSize;
}


string sequence = "+----++++++---++---++";
void OnDeinit(const int reason) {
   if(!InpProduceSequence)
      return;
      
   sequence = "";
   for(int i = 1; i < ArraySize(colorBuffer); i++) {
      double latestPrice = lineBuffer[i];
      double prevPrice = lineBuffer[i-1];

      if(latestPrice > prevPrice) {
         sequence += "+";
      } else
      if(latestPrice < prevPrice) {
         sequence += "-";
      }
   }
   
   int fileHandle = FileOpen("MyRenko"+"//"+InpFileName,FILE_WRITE|FILE_CSV);
   if(fileHandle!=INVALID_HANDLE)
     {
      PrintFormat("file is available for writing");
      PrintFormat("File path: %s\\Files\\",TerminalInfoString(TERMINAL_DATA_PATH));
      //--- first, write the number of signals
      FileWrite(fileHandle,sequence);
      //--- close the file
      FileClose(fileHandle);
      PrintFormat("Data is written, file is closed");
     }
   else
      PrintFormat("Failed to open file, Error code = %d",GetLastError());
}