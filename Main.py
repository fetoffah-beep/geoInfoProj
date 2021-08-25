# -*- coding: utf-8 -*- 
#!/usr/bin/env python

import os
import wx
import wx.xrc
import wx.adv
import geopandas as gpd
import numpy as np
from wx.html import HtmlWindow
from wx.html import HtmlHelpController

# Import defined functions
from functions.ionosphericCorrectionSF import ionoCorrection as iono
from functions.sat_orbit import SatelliteInfo
from functions.read_rinex import readIonosphericParamters as readIono
from functions.read_rinex import read_nav as rNav
from functions.read_rinex import getSatellitePRN as gsp


# Plotting modules
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
# from matplotlib.figure import Figure
import cartopy.crs as ccrs
matplotlib.use('WXAgg')


###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"GNSS Data Processing", pos = wx.DefaultPosition, size = (750,480), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        
        vSizer = wx.BoxSizer( wx.VERTICAL )     # Horinzontal box sizer
        hSizer = wx.BoxSizer( wx.HORIZONTAL )     # Vertival box sizer

        
        self.SetSizer( vSizer )
        self.Layout()
        

        # Add an icon
        icon = wx.Icon('images/gnss.ico', type = wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)

        ###############################################
        # MENU BAR
        ###############################################
        self.MenuBar = wx.MenuBar( 0 )
        self.FileMenu = wx.Menu()

        # File menu and its items
        self.openMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Open"+ u"\t" + u"Ctrl + O", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.openMenu )

        self.FileMenu.AppendSeparator()

        self.closeMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Close"+ u"\t" + u"Alt + F4", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.closeMenu )
        
        self.MenuBar.Append( self.FileMenu, u"&File" ) 
        
        # Menu for the modules and its items
        self.modulesMenu = wx.Menu()
        self.satelliteOrtbitItem = wx.MenuItem( self.modulesMenu, wx.ID_ANY, u"&Satellite Orbit", wx.EmptyString, wx.ITEM_NORMAL )
        self.modulesMenu.Append( self.satelliteOrtbitItem )
        
        self.ionosphericModel = wx.MenuItem( self.modulesMenu, wx.ID_ANY, u"&Ionospheric Model", wx.EmptyString, wx.ITEM_NORMAL )
        self.modulesMenu.Append( self.ionosphericModel )
        
        self.MenuBar.Append( self.modulesMenu, u"&Modules" ) 
        
        # Help menu for the about page and help contents
        self.HelpMenu = wx.Menu()

        self.helpContentMenuItem = wx.MenuItem( self.HelpMenu, wx.ID_ANY, u"&Help Content", wx.EmptyString, wx.ITEM_NORMAL )
        self.HelpMenu.Append( self.helpContentMenuItem )


        self.HelpMenu.AppendSeparator()

        self.aboutMenuItem = wx.MenuItem( self.HelpMenu, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL )
        self.HelpMenu.Append( self.aboutMenuItem )
        
        self.MenuBar.Append( self.HelpMenu, u"&Help" ) 
        
        self.SetMenuBar( self.MenuBar )


        # Create accelerator for the menu buttons, i.e, the shortcuts
        shortCuts = [wx.AcceleratorEntry() for i in range(5)]
        shortCuts[0].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_O, self.openMenu.GetId())
        shortCuts[1].Set(wx.ACCEL_ALT, wx.WXK_F4, self.closeMenu.GetId())
        shortCuts[2].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_K, self.satelliteOrtbitItem.GetId())
        shortCuts[3].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_I, self.ionosphericModel.GetId())
        shortCuts[4].Set(wx.ACCEL_NORMAL, wx.WXK_F1, self.helpContentMenuItem.GetId())

        accel = wx.AcceleratorTable(shortCuts)
        self.SetAcceleratorTable(accel) 


        ##########################################################
        #   NOTEBOOK CONTAINERS
        ##########################################################
        
        self.noteBook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH|wx.NB_TOP )
        # paramNoteBookWindow = paramNoteBookPanel(self.noteBook)
        orbitNoteBookWindow = orbitNoteBookPanel(self.noteBook)
        angleNoteBookWindow = angleNoteBookPanel(self.noteBook)
        ionoNoteBookWindow = ionosphereNoteBookPanel(self.noteBook)
        
        # Add the pages to the noteBook
        # self.noteBook.AddPage(paramNoteBookWindow, 'Input')
        self.noteBook.AddPage(orbitNoteBookWindow, 'Orbit')
        self.noteBook.AddPage(angleNoteBookWindow, 'Angles')
        self.noteBook.AddPage(ionoNoteBookWindow, 'Ionosphere')
        

        vSizer.Add( self.noteBook, 1, wx.EXPAND|wx.ALL, 5 )


        #################################################
        #   STATUS BAR
        #################################################
        self.statusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
        
        self.Centre( wx.BOTH )


        # ---------------------------Connect Events ------------------------------------------------
        # Menu events
        self.Bind( wx.EVT_MENU, self.onOpen, id = self.openMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.CloseFunc, id = self.closeMenu.GetId() )
        # self.Bind( wx.EVT_MENU, self.onOrbit, id = self.satelliteOrtbitItem.GetId() )
        # self.Bind( wx.EVT_MENU, self.ionoModel, id = self.ionosphericModel.GetId() )
        self.Bind( wx.EVT_MENU, self.helpContent, id = self.helpContentMenuItem.GetId() )
        self.Bind( wx.EVT_MENU, self.aboutPage, id = self.aboutMenuItem.GetId() )

        
    def __del__( self ):
        pass

    def onOpen (self, event):
        try:
            file = wx.FileDialog(self, message = "Select a file", defaultDir = os.getcwd(), defaultFile="", wildcard=u"Rinex (*.rnx)|*.rnx| All files(*.)| *.*", style= wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if file.ShowModal() != wx.ID_OK:
                return
            MainFrame.onOpen.filePath = file.GetPath()

            #Get the available satellite PRN in the file
            MainFrame.onOpen.satellitePRN =   gsp( MainFrame.onOpen.filePath )

            file.Destroy()

        except Exception as err:
            dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return


    def aboutPage(self, event):
        dlg = AboutPage(self)
        dlg.ShowModal()
        dlg.Destroy()

  

    def helpContent( self, event ):
        html  = HtmlHelpController(style=wx.html.HF_TOOLBAR | wx.html.HF_CONTENTS | wx.html.HF_INDEX | wx.html.HF_SEARCH | wx.html.HF_PRINT, parentWindow=None)
        html.AddBook(u"Document/User Manual.hhp")
        html.Display(u"Document/Table Of Contents.hhc")
        html.Show()

    def CloseFunc( self, event ):
        self.Close()


class AboutPage(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id = wx.ID_ANY, title = 'About GNSS Data Processing SOFTWARE', pos = wx.DefaultPosition, size = wx.Size( 350,410 ), style = wx.DEFAULT_DIALOG_STYLE )
        html  = wx.html.HtmlWindow(self)
        html.LoadPage(u"functions/about.html")


###########################################################################
##  Note Book Classes
###########################################################################

# -------------------------------Input-----------------------------------#
class paramNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        # Create the static box for receiving parameters for the functionalities
        paramStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Open Navigation Message" ), wx.VERTICAL )
        # Add the static box to the sizer
        noteBookSizer.Add( paramStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        # Add spacer for a nicer view
        paramStaticbox.AddSpacer(10)
        
        
        # # Widgets for entering parameters for file opening
        satSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        self.paramStaticText = wx.StaticText( paramStaticbox.GetStaticBox(), wx.ID_ANY, u"Select rinex file to process: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.paramStaticText.Wrap( -1 )
        satSizer1.Add( self.paramStaticText, 0, wx.ALL, 5 )

        
        self.satelliteFilePicker = wx.FilePickerCtrl( paramStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"Rinex (*.rnx)|*.rnx| All files(*.)| *.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
        satSizer1.Add( self.satelliteFilePicker, 0, wx.TOP|wx.RIGHT|wx.LEFT, 5 )
        paramStaticbox.Add( satSizer1, 0, wx.EXPAND, 5 )
        #path=self.satelliteFilePicker.GetPath()

         
        self.SetSizer( noteBookSizer )
        self.Layout()

# -------------------------------Satellite orbit parameter------------------------------#             
class orbitNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # Create the static box for receiving parameters for the functionalities
        satelliteStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Satellite Orbit Parameters" ), wx.VERTICAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( satelliteStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        
        
        # Widgets for entering parameters for satellite orbit modelling
        # Add spacer for a nicer view
        satelliteStaticbox.AddSpacer(10)

        satSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.prnStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter prn number of SV (eg: 01, 02, 15):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.prnStaticText.Wrap( -1 )
        satSizer2.Add( self.prnStaticText, 0, wx.ALL, 5 )
        
        self.prnTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer2.Add( self.prnTextCtrl, 0, wx.ALL, 5 )


        # self.orbitChoicesChoices = [ u" " ]
        # # self.orbitChoicesChoices.extend( MainFrame.onOpen.satellitePRN )
        # self.orbitChoices = wx.Choice( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.orbitChoicesChoices, wx.CB_SORT )
        # satSizer2.Add( self.orbitChoices, 0, wx.ALL, 5 )

        
        
        satelliteStaticbox.Add( satSizer2, 0, wx.ALL, 5 )
        
        satelliteStaticbox.AddSpacer(150)


        self.orbitPoceedButton = wx.Button( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        satelliteStaticbox.Add( self.orbitPoceedButton, 0, wx.ALL, 5 )
        

        # Connected events
        self.orbitPoceedButton.Bind( wx.EVT_BUTTON, self.OrbitCompute )
        
        
        self.SetSizer( noteBookSizer )
        self.Layout()


    def OrbitCompute(self, event):
        try:
            plt.clf()  #clears figure
            filePath = MainFrame.onOpen.filePath
            if os.path.splitext(filePath)[1] != '.rnx':
                dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

            svPRN = self.prnTextCtrl.GetValue()

            satelliteOrbit = SatelliteInfo( filePath, svPRN )

            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.stock_img()
            #ax.coastlines()
            ax.gridlines()
            
            plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'r', linewidth=3, transform=ccrs.Geodetic())
            font1={'family':'serif','color':'black','size':15}
            first_epc=str(satelliteOrbit.first_epoch)
            last_epc=str(satelliteOrbit.last_epoch)
            plt.title('Satellite G'+str(svPRN)+'\n(from  '+first_epc+'  to  '+last_epc+')', fontdict=font1)
            #plt.suptitle()
            plt.show()

        except Exception as err:
            dlg = wx.MessageDialog(None, 'No navigation file (.rnx)/existing satellite has been selected \n Click File -> Open to select file', 'File Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return


#---------------------------------Angles analysis---------------------------------#
class angleNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        # Create the static box for receiving parameters for the functionalities
        satelliteStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Angles Analysis" ), wx.VERTICAL )
        # Add the static box to the sizer
        noteBookSizer.Add( satelliteStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        
        # Widgets for entering parameters for satellite orbit modelling
        # Add spacer for a nicer view
        satelliteStaticbox.AddSpacer(10)
        
        satSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        self.prnStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter prn number of SV (eg: 01, 02, 15):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.prnStaticText.Wrap( -1 )
        satSizer2.Add( self.prnStaticText, 0, wx.ALL, 5 )
        self.prnTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer2.Add( self.prnTextCtrl, 0, wx.ALL, 5 )
        satelliteStaticbox.Add( satSizer2, 0, wx.ALL, 5 )
        
        satelliteStaticbox.AddSpacer(10)
        
        satSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        self.refStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter position of reference point:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.refStaticText.Wrap( -1 )
        satSizer3.Add( self.refStaticText, 0, wx.ALL, 5 )
        satelliteStaticbox.Add( satSizer3, 0, wx.ALL, 5 )
        
        satSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        self.xStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"x", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.xStaticText.Wrap( -1 )
        satSizer4.Add( self.xStaticText, 0, wx.ALL, 5 )
        self.xTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer4.Add( self.xTextCtrl, 0, wx.ALL, 5 )
        satelliteStaticbox.Add( satSizer4, 0, wx.ALL, 5 )
        
        satSizer5 = wx.BoxSizer( wx.HORIZONTAL )
        self.yStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"y", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.yStaticText.Wrap( -1 )
        satSizer5.Add( self.yStaticText, 0, wx.ALL, 5 )
        self.yTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer5.Add( self.yTextCtrl, 0, wx.ALL, 5 )
        satelliteStaticbox.Add( satSizer5, 0, wx.ALL, 5 )
        
        satSizer6 = wx.BoxSizer( wx.HORIZONTAL )
        self.zStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"z", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.zStaticText.Wrap( -1 )
        satSizer6.Add( self.zStaticText, 0, wx.ALL, 5 )
        self.zTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer6.Add( self.zTextCtrl, 0, wx.ALL, 5 )
        satelliteStaticbox.Add( satSizer6, 0, wx.ALL, 5 )
        
        satelliteStaticbox.AddSpacer(30)
          
        self.orbitPoceedButton = wx.Button( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        satelliteStaticbox.Add( self.orbitPoceedButton, 0, wx.ALL, 5 )
        

        # Connected events
        self.orbitPoceedButton.Bind( wx.EVT_BUTTON, self.AnglesCompute )
        
        
        self.SetSizer( noteBookSizer )
        self.Layout()
         
        #self.SetSizer( noteBookSizer )
        self.Layout()
        
        
    def AnglesCompute(self, event):
        plt.clf()  #clears figure
        filePath = MainFrame.onOpen.filePath
        if os.path.splitext(filePath)[1] != '.rnx':
            dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return

        svPRN = self.prnTextCtrl.GetValue()
        x = self.xTextCtrl.GetValue()
        y = self.yTextCtrl.GetValue()
        z = self.zTextCtrl.GetValue()

        Angles = SatelliteInfo( filePath, svPRN, x, y, z )
        #plot using Angles.epochs, Angles.azimuth and Angles.elevation

        
        
        
# ------------------------------- Ionospheric Error Parameter ------------------------------#             

class ionosphereNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # Create the static box for receiving parameters for the functionalities
        ionosphereStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Ionosphere Parameters" ), wx.VERTICAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( ionosphereStaticbox, 1, wx.ALL|wx.EXPAND, 15 )

       
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)


        # ----------------------------- MODE -----------------------------#
        modeSelectionSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.choiceStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Preferred Mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.choiceStaticText.Wrap( -1 )
        modeSelectionSizer.Add( self.choiceStaticText, 0, wx.ALL, 5 )
        
        choiceChoices = [ u"Globe analysis", u"Station analysis" ]
        self.choice = wx.Choice( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceChoices, wx.CB_SORT )
        modeSelectionSizer.Add( self.choice, 0, wx.ALL, 5 )

        ionosphereStaticbox.Add( modeSelectionSizer, 0, 0, 5 )
        
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        
        # ----------------------------- TIME -----------------------------#
        timeSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.timeStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Time (HH:MM:SS)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.timeStaticText.Wrap( -1 )
        timeSizer.Add( self.timeStaticText, 0, wx.ALL, 5 )

        self.timeHHControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=24, initial=0)
        timeSizer.Add( self.timeHHControl, 0, wx.ALL, 5 )

        self.timeMMControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0)
        timeSizer.Add( self.timeMMControl, 0, wx.ALL, 5 )

        self.timeSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0)
        timeSizer.Add( self.timeSSControl, 0, wx.ALL, 5 )
        
       
        ionosphereStaticbox.Add( timeSizer, 0, 0, 5 )

        # ----------------------------- ELEVATION -----------------------------#
        
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        elevSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.elevStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Elevation angle (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.elevStaticText.Wrap( -1 )
        elevSizer.Add( self.elevStaticText, 0, wx.ALL, 5 )

        self.elevDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=90, initial=0 )
        elevSizer.Add( self.elevDegControl, 0, wx.ALL, 5 )

        self.elevMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0 )
        elevSizer.Add( self.elevMinControl, 0, wx.ALL, 5 )

        self.elevSSControl = wx.SpinCtrlDouble(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0, inc=0.001)
        elevSizer.Add( self.elevSSControl, 0, wx.ALL, 5 )

        ionosphereStaticbox.Add( elevSizer, 0, 0, 5 )

        
        # ----------------------------- AZIMUTH -----------------------------#
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)
        
        azimuthSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.azStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Azimuth (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.azStaticText.Wrap( -1 )
        azimuthSizer.Add( self.azStaticText, 0, wx.ALL, 5 )

        self.azDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=-180, max=180, initial=0 )
        azimuthSizer.Add( self.azDegControl, 0, wx.ALL, 5 )

        self.azMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0 )
        azimuthSizer.Add( self.azMinControl, 0, wx.ALL, 5 )

        self.azSSControl = wx.SpinCtrlDouble(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0, inc=0.001)
        azimuthSizer.Add( self.azSSControl, 0, wx.ALL, 5 )

 
        ionosphereStaticbox.Add( azimuthSizer, 0, wx.EXPAND, 5 )

        

        # ----------------------------- LONGITUDE -----------------------------#
        
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        longSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.longStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Longitude (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.longStaticText.Wrap( -1 )
        longSizer.Add( self.longStaticText, 0, wx.ALL, 5 )
        
        self.longDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=-180, max=180, initial=0 )
        longSizer.Add( self.longDegControl, 0, wx.ALL, 5 )

        self.longMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0 )
        longSizer.Add( self.longMinControl, 0, wx.ALL, 5 )

        self.longSSControl = wx.SpinCtrlDouble(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP , min=0, max=60, initial=0, inc=0.001)
        longSizer.Add( self.longSSControl, 0, wx.ALL, 5 )
        
        
        ionosphereStaticbox.Add( longSizer, 0, 0, 5 )


        # ----------------------------- LATITUDE -----------------------------#
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        latitudeSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.latStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Latitude (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.latStaticText.Wrap( -1 )
        latitudeSizer.Add( self.latStaticText, 0, wx.ALL, 5 )
        
        self.latDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=-90, max=90, initial=0 )
        latitudeSizer.Add( self.latDegControl, 0, wx.ALL, 5 )

        self.latMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0 )
        latitudeSizer.Add( self.latMinControl, 0, wx.ALL, 5 )

        self.latSSControl = wx.SpinCtrlDouble(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"00", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS | wx.SP_WRAP, min=0, max=60, initial=0, inc=0.001 )
        latitudeSizer.Add( self.latSSControl, 0, wx.ALL, 5 )
        
        
        ionosphereStaticbox.Add( latitudeSizer, 0, 0, 5 )


        # Show the relevant boxes after the mode has been selected by the user
        wx.CallAfter(self.timeStaticText.Show, False)
        wx.CallAfter(self.timeHHControl.Show, False)
        wx.CallAfter(self.timeMMControl.Show, False)
        wx.CallAfter(self.timeSSControl.Show, False)
        wx.CallAfter(self.elevStaticText.Show, False)
        wx.CallAfter(self.elevDegControl.Show, False)
        wx.CallAfter(self.elevMinControl.Show, False)
        wx.CallAfter(self.elevSSControl.Show, False)
        wx.CallAfter(self.azStaticText.Show, False)
        wx.CallAfter(self.azDegControl.Show, False)
        wx.CallAfter(self.azMinControl.Show, False)
        wx.CallAfter(self.azSSControl.Show, False)
        wx.CallAfter(self.longStaticText.Show, False)
        wx.CallAfter(self.longDegControl.Show, False)
        wx.CallAfter(self.longMinControl.Show, False)
        wx.CallAfter(self.longSSControl.Show, False)
        wx.CallAfter(self.latStaticText.Show, False)
        wx.CallAfter(self.latDegControl.Show, False)
        wx.CallAfter(self.latMinControl.Show, False)
        wx.CallAfter(self.latSSControl.Show, False)

        self.proceedButton = wx.Button( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        ionosphereStaticbox.Add( self.proceedButton, 0, wx.ALL, 5 )
        


        # Connected events
        self.choice.Bind( wx.EVT_CHOICE, self.OnChoice )
        self.proceedButton.Bind( wx.EVT_BUTTON, self.IonosphereCompute )
        
        self.SetSizer( noteBookSizer )
        self.Layout()

    def IonosphereCompute( self, event ):
        try:
            filePath = MainFrame.onOpen.filePath
            if os.path.splitext(filePath)[1] != '.rnx':
                dlg = wx.MessageDialog(None, 'Selected file is not of Navigation type (.rnx)', 'File Type Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
                dlg.ShowModal()
                dlg.Destroy()
                return

        except Exception as err:
            dlg = wx.MessageDialog(None, 'No navigation file (.rnx) has been selected \n \n Click File -> Open to select file', 'File Error', wx.OK | wx.ICON_ERROR, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return
        
        # ---------------------COMPUTE IONO CORR-----------------------------------------
        ionoParams = readIono( filePath )

        if len(ionoParams) == 0:
            dlg = wx.MessageDialog(None, 'Selected file does not have Ionospheric  Correction Parameters', 'Information', wx.OK|wx.ICON_INFORMATION, wx.DefaultPosition )
            dlg.ShowModal()
            dlg.Destroy()
            return

        
        # ---------------------PLOT IONO MAP -----------------------------------------
        if self.choice.GetStringSelection() == 'Station analysis':
            elevation = np.linspace(0, 90, 181)
            azimuth = np.linspace(-180, 180, 721)
            longitude = self.longDegControl.GetValue() + self.longMinControl.GetValue() / 60 + self.longSSControl.GetValue() / 3600
            latitude = self.latDegControl.GetValue() + self.latMinControl.GetValue() / 60 + self.latSSControl.GetValue() / 3600
            time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
            
            stationPoints = np.zeros((len(elevation), len(azimuth)))

            for elev in range(len(elevation)):
                for azim in range(len(azimuth)):
                    stationPoints[elev][azim] = iono(latitude, longitude, azimuth[azim], elevation[elev], time, ionoParams[0])
            
            x,y = np.meshgrid(azimuth, elevation)

            x = x * np.pi / 180
            y = np.flip( y * np.pi / 180, 1 )

            stationPoints = np.flip( stationPoints, (0,1) )

            fig1, ax2 = plt.subplots(subplot_kw=dict(projection='polar'), constrained_layout=False)
            CS = ax2.contourf(x, y, stationPoints, 100, cmap=cm.rainbow)
            ax2.set_theta_zero_location('S')
            ax2.set_theta_direction(-1)
            ax2.set_title('Ionospheric delay at time = {} : {} : {} '.format( self.timeHHControl.GetValue(), self.timeMMControl.GetValue(), self.timeSSControl.GetValue()))
            ax2.set_ylim(0, np.pi/2)


 



            




















           
        else:
            elevation = self.elevDegControl.GetValue() + self.elevMinControl.GetValue() / 60 + self.elevSSControl.GetValue() / 3600
            azimuth = self.azDegControl.GetValue() + self.azMinControl.GetValue() / 60 + self.azSSControl.GetValue() / 3600
            longitude = np.linspace(-180, 180, 721) 
            latitude = np.linspace(-90, 90, 361) 
            time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
            
            stationPoints = np.zeros((len(latitude), len(longitude)))
            
            
            for lat in range(len(latitude)):
                for longit in range(len(longitude)):
                    stationPoints[lat][longit] = iono(latitude[lat], longitude[longit], azimuth, elevation, time, ionoParams[0])
            
            x,y = np.meshgrid(longitude, latitude)
            
        
            fig1, ax2 = plt.subplots(constrained_layout=False)

            worldMap = gpd.read_file(r'worldMap/ne_10m_admin_0_countries.shp')

            CS = ax2.contourf(x, y, stationPoints, 100, cmap=cm.rainbow)
        
            ax2.set_title('Ionospheric delay at time = {} : {} : {} '.format( self.timeHHControl.GetValue(), self.timeMMControl.GetValue(), self.timeSSControl.GetValue()))
            ax2.set_xlabel('Longitude (\u00B0)')
            ax2.set_ylabel('Latitude (\u00B0)')
            ax2.set_xlim([-180, 180])
            ax2.set_ylim([-90, 90])
            worldMap.plot(ax=ax2, facecolor='none', edgecolor='black', lw=0.15)

        cbar = plt.colorbar(CS)
  
       

        ionoMap = plt.show()
        


    def OnChoice (self, event):
        self.user_choice = event.GetString()
        if self.user_choice == 'Station analysis':
            self.timeStaticText.Show(True)
            self.timeHHControl.Show(True)
            self.timeMMControl.Show(True)
            self.timeSSControl.Show(True)
            self.elevStaticText.Show(True)
            self.elevDegControl.Show(False)
            self.elevMinControl.Show(False)
            self.elevSSControl.Show(False)
            self.azStaticText.Show(True)
            self.azDegControl.Show(False)
            self.azMinControl.Show(False)
            self.azSSControl.Show(False)
            self.longStaticText.Show(True)
            self.longDegControl.Show(True)
            self.longMinControl.Show(True)
            self.longSSControl.Show(True)
            self.latStaticText.Show(True)
            self.latDegControl.Show(True)
            self.latMinControl.Show(True)
            self.latSSControl.Show(True)
        else:
            self.timeStaticText.Show(True)
            self.timeHHControl.Show(True)
            self.timeMMControl.Show(True)
            self.timeSSControl.Show(True)
            self.elevStaticText.Show(True)
            self.elevDegControl.Show(True)
            self.elevMinControl.Show(True)
            self.elevSSControl.Show(True)
            self.azStaticText.Show(True)
            self.azDegControl.Show(True)
            self.azMinControl.Show(True)
            self.azSSControl.Show(True)
            self.longStaticText.Show(True)
            self.longDegControl.Show(False)
            self.longMinControl.Show(False)
            self.longSSControl.Show(False)
            self.latStaticText.Show(True)
            self.latDegControl.Show(False)
            self.latMinControl.Show(False)
            self.latSSControl.Show(False)

 
###########################################################################
## RUN THE MODEL
###########################################################################

# check that the module is being run as a program and imported   
if __name__ == '__main__':
    app = wx.App()
    # The main frame object is created after creating the application object as the app is needed for the frame to execute
    frame = MainFrame(None)
    frame.Show()
    #frame.Maximize(True)        # Maximize the window on first load
    app.MainLoop()