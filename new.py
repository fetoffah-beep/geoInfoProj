# -*- coding: utf-8 -*- 
#!/usr/bin/env python

import wx
import wx.xrc
import os
import wx.adv
import numpy as np
# from Map import DrawFrame as DF
from functions.ionosphericCorrectionSF import ionoCorrection as iono
from functions.sat_orbit import SatelliteInfo
from functions.read_rinex import readIonosphericParamters as readIono
from functions.read_rinex import read_nav as rNav


import geopandas as gpd

# Plotting modules
import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure


# # create a world map
# worldmap =  pygal.maps.world.World()
# worldmap.render()
# worldmap.render_to_file('abc.jpg')

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
    
    def __init__( self, parent ):
        #wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"GNSS Data Processing", pos = wx.DefaultPosition, size =  (wx.DefaultSize), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"GNSS Data Processing", pos = wx.DefaultPosition, size = (800,500), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        vSizer = wx.BoxSizer( wx.VERTICAL )     # Horinzontal box sizer
        hSizer = wx.BoxSizer( wx.HORIZONTAL )     # Vertival box sizer
        
        self.SetSizer( vSizer )
        self.Layout()
        self.MenuBar = wx.MenuBar( 0 )
        self.FileMenu = wx.Menu()

        # Add an icon
        icon = wx.Icon('images/gnss.ico', type = wx.BITMAP_TYPE_ANY)
        self.SetIcon(icon)

        # File menu and its items
        self.openMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Open"+ u"\t" + u"Ctrl + O", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.openMenu )
        
        self.runMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Run" + u"\t" + u"Ctrl + R", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.runMenu )
        
        self.saveMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Save"+ u"\t" + u"Ctrl + S", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.saveMenu )
        
        self.saveAsMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Save as.."+ u"\t" + u"Ctrl + Shift + S", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.saveAsMenu )
        
        self.printMenu = wx.MenuItem( self.FileMenu, wx.ID_ANY, u"&Print"+ u"\t" + u"Ctrl + P", wx.EmptyString, wx.ITEM_NORMAL )
        self.FileMenu.Append( self.printMenu )
        
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
        
        self.troposphericModel = wx.MenuItem( self.modulesMenu, wx.ID_ANY, u"&Tropospheric Model", wx.EmptyString, wx.ITEM_NORMAL )
        self.modulesMenu.Append( self.troposphericModel )
        
        self.MenuBar.Append( self.modulesMenu, u"&Modules" ) 
        
        # Help menu for the about page
        self.HelpMenu = wx.Menu()
        self.aboutMenuItem = wx.MenuItem( self.HelpMenu, wx.ID_ANY, u"&About", wx.EmptyString, wx.ITEM_NORMAL )
        self.HelpMenu.Append( self.aboutMenuItem )
        
        self.MenuBar.Append( self.HelpMenu, u"&Help" ) 
        
        self.SetMenuBar( self.MenuBar )

# ----------------------------------------------------------------------------------------------
        # NoteBooks as container for the drawing widgets
        
        self.noteBook = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_FIXEDWIDTH|wx.NB_TOP )
        satNoteBookWindow = SatelliteNoteBookPanel(self.noteBook)
        ionoNoteBookWindow = IonosphericNoteBookPanel(self.noteBook)
        pProsNoteBookWindow = PreProcessingNoteBookPanel(self.noteBook)
        outNoteBookWindow = OutputNoteBookPanel(self.noteBook)

        # Add the pages to the noteBook
        self.noteBook.AddPage(satNoteBookWindow, 'Satellite')
        self.noteBook.AddPage(ionoNoteBookWindow, 'Ionosphere')
        self.noteBook.AddPage(pProsNoteBookWindow, 'Processing')
        self.noteBook.AddPage(outNoteBookWindow, 'Output')


        vSizer.Add( self.noteBook, 1, wx.EXPAND|wx.ALL, 5 )


# ----------------------------------------------------------------------------------------------

        # Create Status bar
        self.statusBar = self.CreateStatusBar( 1, 0, wx.ID_ANY )
        
        self.Centre( wx.BOTH )

# ----------------------------------------------------------------------------------------------        
        # Connect Events
        # Menu events
        self.Bind( wx.EVT_MENU, self.onOpen, id = self.openMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.onRun, id = self.runMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.onSave, id = self.saveMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.onSaveAs, id = self.saveAsMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.onPrint, id = self.printMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.CloseFunc, id = self.closeMenu.GetId() )
        self.Bind( wx.EVT_MENU, self.onOrbit, id = self.satelliteOrtbitItem.GetId() )
        self.Bind( wx.EVT_MENU, self.ionoModel, id = self.ionosphericModel.GetId() )
        self.Bind( wx.EVT_MENU, self.tropoModel, id = self.troposphericModel.GetId() )
        self.Bind( wx.EVT_MENU, self.aboutPage, id = self.aboutMenuItem.GetId() )

        # Notebook events
        self.noteBook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged )
        self.noteBook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGING, self.OnPageChanging )
        
    
        
        # Create accelerator for the menu buttons, i.e, the shortcuts
        shortCuts = [wx.AcceleratorEntry() for i in range(6)]

        shortCuts[0].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_O, self.openMenu.GetId())
        shortCuts[1].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_R, self.runMenu.GetId())
        shortCuts[2].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_S, self.saveMenu.GetId())
        shortCuts[3].Set(wx.ACCEL_CTRL|wx.ACCEL_SHIFT, wx.WXK_CONTROL_S, self.saveAsMenu.GetId())
        shortCuts[4].Set(wx.ACCEL_CTRL, wx.WXK_CONTROL_P, self.printMenu.GetId())
        shortCuts[5].Set(wx.ACCEL_ALT, wx.WXK_F4, self.closeMenu.GetId())
        

        accel = wx.AcceleratorTable(shortCuts)
        self.SetAcceleratorTable(accel) 



        def __del__( self ):
            pass
    
    # Event handlers
    def onOpen (self, event):
        file = wx.FileDialog(self, message = "Choose a file", defaultDir = os.getcwd(), defaultFile="", wildcard=u"Rinex (*.rnx)|*.rnx| All files(*.)| *.*", style= wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if file.ShowModal() == wx.ID_OK:
            filePath = file.GetPath()
            self.ionoParam = readIono( filePath )
            
        else:
            return

        file.Destroy()


    def onRun( self, event ):
        event.Skip()
    
    def onSave( self, event ):
        pass
        # if not self.filename:
        #     self.OnSaveAs(event)
        # else:
        #     self.SaveFile()
    
    def onSaveAs( self, event ):
        event.Skip()
    
    def onPrint( self, event ):
        event.Skip()
    
    def onOrbit( self, event ):
        event.Skip()
    
    def ionoModel( self, event ):
        event.Skip()
    
    def tropoModel( self, event ):
        event.Skip()

    def CloseFunc( self, event ):
        self.Close()
    
    # Function to contain the about page dialog box
    def aboutPage(self, event):
        # aboutInfo = wx.adv.AboutDialogInfo()
        # aboutInfo.SetName("GNSS Data Processing")
        # aboutInfo.SetVersion('Version 1.0')
        # aboutInfo.SetDescription(("""This software estimates the position of a \n satellite by reading the observation data of RINEX\n format as well as the ephemerides information.\n The project has been carried out for the Geoinformatics\n Project course under the supervision of Prof. Ludovico Biagi!"""))
        # aboutInfo.SetCopyright("(C) 2021")
        # aboutInfo.SetWebSite("https://www.polimi.it/")
        # aboutInfo.AddDeveloper("Felix Enyimah Toffah")
        # aboutInfo.AddDeveloper("Alessandro Gatti")

        # wx.adv.AboutBox(aboutInfo)
        
        diag = wx.Dialog(None, id = wx.ID_ANY, title = 'About GNSS Data Processing SOFTWARE', pos = wx.DefaultPosition, size = wx.Size( 300,400 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        diag.SetSizeHints( wx.Size( 300,400 ), wx.Size( 300,400 ) )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        diag.m_bitmap1 = wx.StaticBitmap( diag, wx.ID_ANY, wx.Bitmap( u"images/polimi.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer2.Add( diag.m_bitmap1, 0, wx.ALL|wx.EXPAND, 5 )
        
        diag.m_staticText1 = wx.StaticText( diag, wx.ID_ANY, u"This software estimates the position of a satellite by reading the observation data of RINEX format as well as the ephemerides information.\nThe project has been carried out for the Geoinformatics Project course under the supervision of Prof. Ludovico Biagi. ", wx.DefaultPosition, wx.DefaultSize, 0 )
        diag.m_staticText1.Wrap( -1 )
        diag.m_staticText1.SetFont( wx.Font( 11, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer2.Add( diag.m_staticText1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        diag.m_staticText2 = wx.StaticText( diag, wx.ID_ANY, u"Developers:\n - Felix Enyimah Toffah \n - Alessandro Gatti", wx.DefaultPosition, wx.DefaultSize, 0 )
        diag.m_staticText2.Wrap( -1 )
        diag.m_staticText2.SetFont( wx.Font( 11, 70, 90, 90, False, wx.EmptyString ) )
        
        bSizer2.Add( diag.m_staticText2, 0, wx.ALL|wx.EXPAND, 5 )
        
        diag.m_staticline1 = wx.StaticLine( diag, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer2.Add( diag.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
        
        diag.m_staticText3 = wx.StaticText( diag, wx.ID_ANY, u"© 2021", wx.DefaultPosition, wx.DefaultSize, 0 )
        diag.m_staticText3.Wrap( -1 )
        bSizer2.Add( diag.m_staticText3, 0, wx.ALL|wx.ALIGN_RIGHT, 5 )
        
        
        diag.SetSizer( bSizer2 )
        diag.Layout()
        
        diag.Centre( wx.BOTH )

        diag.Show()

    def OnPageChanged(self, event):
        event.Skip()

    def OnPageChanging(self, event):
        event.Skip()

 
###########################################################################
## Class Note Book 
###########################################################################
       
class SatelliteNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Create the sizer
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # Create the static box for receiving parameters for the functionalities
        satelliteStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Satellite Orbit Parameters" ), wx.VERTICAL )
        # troposphereStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Troposphere Parameters" ), wx.VERTICAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( satelliteStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        # noteBookSizer.Add( troposphereStaticbox, 1, wx.ALL|wx.EXPAND, 15 )


        ############################################
        # Satellite orbit parameter
        ############################################
        # Widgets for entering parameters for satellite orbit modelling
        # Add spacer for a nicer view
        satelliteStaticbox.AddSpacer(10)
        satSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        self.satelliteStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Select rinex file to process: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.satelliteStaticText.Wrap( -1 )
        satSizer1.Add( self.satelliteStaticText, 0, wx.ALL, 5 )

        
        self.satelliteFilePicker = wx.FilePickerCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a file", u"Rinex (*.rnx)|*.rnx| All files(*.)| *.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
        satSizer1.Add( self.satelliteFilePicker, 0, wx.TOP|wx.RIGHT|wx.LEFT, 5 )
        satelliteStaticbox.Add( satSizer1, 0, wx.EXPAND, 5 )
        
        # Add spacer for a nicer view
        satelliteStaticbox.AddSpacer(10)


        satSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.timeStaticText = wx.StaticText( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Enter prn number of SV (eg: 01, 02, 15):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.timeStaticText.Wrap( -1 )
        satSizer2.Add( self.timeStaticText, 0, wx.ALL, 5 )
        
        self.prnTextCtrl = wx.TextCtrl( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        satSizer2.Add( self.prnTextCtrl, 0, wx.ALL, 5 )
        
        
        satelliteStaticbox.Add( satSizer2, 0, wx.ALL, 5 )
        
        satelliteStaticbox.AddSpacer(150)


        self.orbitPoceedButton = wx.Button( satelliteStaticbox.GetStaticBox(), wx.ID_ANY, u"Proceed", wx.DefaultPosition, wx.DefaultSize, 0 )
        satelliteStaticbox.Add( self.orbitPoceedButton, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        
        
        
       
        # Connected events
        self.orbitPoceedButton.Bind( wx.EVT_BUTTON, self.OrbitCompute )
        # self.svPRNbutton.Bind( wx.EVT_BUTTON, self.OrbitCompute )
        
        

        ########################################################################################
        # Troposphere parameter
        ########################################################################################

        
        
        self.SetSizer( noteBookSizer )
        self.Layout()
        
# -------------------------------------------
    def OrbitCompute(self, event):
        filePath = self.satelliteFilePicker.GetPath()
        ionoParams = readIono( filePath )
        svPRN = self.prnTextCtrl.GetValue()

        satelliteOrbit = SatelliteInfo( filePath, svPRN )

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        
        plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'r', transform=ccrs.Geodetic())
        font1={'family':'serif','color':'black','size':15}
        first_epc=str(satelliteOrbit.first_epoch)
        last_epc=str(satelliteOrbit.last_epoch)
        plt.title('Satellite G'+str(svPRN)+'\n(from  '+first_epc+'  to  '+last_epc+')', fontdict=font1)
        #plt.suptitle()
        plt.show()





class IonosphericNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        noteBookSizer = wx.BoxSizer( wx.HORIZONTAL )
        ionosphereStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Ionosphere Parameters" ), wx.VERTICAL )
        # troposphereStaticbox = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Troposphere Parameters" ), wx.VERTICAL )
        
        # Add the static box to the sizer
        noteBookSizer.Add( ionosphereStaticbox, 1, wx.ALL|wx.EXPAND, 15 )
        
        ########################################################################################
        # Ionosphere parameter
        ########################################################################################
       
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)


        modeSelectionSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.choiceStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Mode:", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.choiceStaticText.Wrap( -1 )
        modeSelectionSizer.Add( self.choiceStaticText, 0, wx.ALL, 5 )
        
        choiceComboBoxChoices = [ u"Station analysis", u"Globe analysis" ]
        self.choiceComboBox = wx.ComboBox( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Select your prefered mode", wx.DefaultPosition, wx.DefaultSize, choiceComboBoxChoices, 0 )
        modeSelectionSizer.Add( self.choiceComboBox, 0, wx.ALL, 5 )
        
        
        ionosphereStaticbox.Add( modeSelectionSizer, 0, 0, 5 )

        

        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)
        
        timeSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.timeStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Time (HH:MM:SS)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.timeStaticText.Wrap( -1 )
        timeSizer.Add( self.timeStaticText, 0, wx.ALL, 5 )

        self.timeHHControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Hour", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=24, initial=0)
        timeSizer.Add( self.timeHHControl, 0, wx.ALL, 5 )

        self.timeMMControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        timeSizer.Add( self.timeMMControl, 0, wx.ALL, 5 )

        self.timeSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Sec", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        timeSizer.Add( self.timeSSControl, 0, wx.ALL, 5 )
        
       
        ionosphereStaticbox.Add( timeSizer, 0, 0, 5 )

        # --------------------------------------------------------------------------------

        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        elevSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        
        self.elevStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Elevation angle (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.elevStaticText.Wrap( -1 )
        elevSizer.Add( self.elevStaticText, 0, wx.ALL, 5 )

        self.elevDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Deg", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=90, initial=0)
        elevSizer.Add( self.elevDegControl, 0, wx.ALL, 5 )

        self.elevMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        elevSizer.Add( self.elevMinControl, 0, wx.ALL, 5 )

        self.elevSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Sec", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        elevSizer.Add( self.elevSSControl, 0, wx.ALL, 5 )

        ionosphereStaticbox.Add( elevSizer, 0, 0, 5 )

        

        # --------------------------------------------------------------------------------
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)
        
        azimuthSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.azStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Azimuth (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.azStaticText.Wrap( -1 )
        azimuthSizer.Add( self.azStaticText, 0, wx.ALL, 5 )

        self.azDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Deg", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=-180, max=180, initial=0)
        azimuthSizer.Add( self.azDegControl, 0, wx.ALL, 5 )

        self.azMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        azimuthSizer.Add( self.azMinControl, 0, wx.ALL, 5 )

        self.azSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Sec", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        azimuthSizer.Add( self.azSSControl, 0, wx.ALL, 5 )

 
        ionosphereStaticbox.Add( azimuthSizer, 0, wx.EXPAND, 5 )

        

        # --------------------------------------------------------------------------------
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        longSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.longStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Longitude (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.longStaticText.Wrap( -1 )
        longSizer.Add( self.longStaticText, 0, wx.ALL, 5 )
        
        self.longDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Deg", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=-180, max=180, initial=0)
        longSizer.Add( self.longDegControl, 0, wx.ALL, 5 )

        self.longMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        longSizer.Add( self.longMinControl, 0, wx.ALL, 5 )

        self.longSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Sec", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        longSizer.Add( self.longSSControl, 0, wx.ALL, 5 )

        
        
        
        ionosphereStaticbox.Add( longSizer, 0, 0, 5 )
        


        # --------------------------------------------------------------------------------
        # Add spacer for a nicer view
        ionosphereStaticbox.AddSpacer(10)

        latitudeSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        self.latStaticText = wx.StaticText( ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Latitude (deg, min, sec)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.latStaticText.Wrap( -1 )
        latitudeSizer.Add( self.latStaticText, 0, wx.ALL, 5 )
        
        self.latDegControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Deg", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=-90, max=90, initial=0)
        latitudeSizer.Add( self.latDegControl, 0, wx.ALL, 5 )

        self.latMinControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        latitudeSizer.Add( self.latMinControl, 0, wx.ALL, 5 )

        self.latSSControl = wx.SpinCtrl(ionosphereStaticbox.GetStaticBox(), wx.ID_ANY, u"Sec", wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
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
        ionosphereStaticbox.Add( self.proceedButton, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        

        # Connected events
        self.choiceComboBox.Bind( wx.EVT_COMBOBOX, self.OnCombo )
        self.proceedButton.Bind( wx.EVT_BUTTON, self.IonosphereCompute )
        # self.svPRNbutton.Bind( wx.EVT_BUTTON, self.OrbitCompute )
        
        self.SetSizer( noteBookSizer )
        self.Layout()
        
    def IonosphereCompute( self, event ):
        if self.choiceComboBox.GetValue() == 'Station analysis':
            elevation = np.linspace(0, 90, 181)
            azimuth = np.linspace(-180, 180, 721)
            longitude = self.longDegControl.GetValue() + self.longMinControl.GetValue() / 60 + self.longSSControl.GetValue() / 3600
            latitude = self.latDegControl.GetValue() + self.latMinControl.GetValue() / 60 + self.latSSControl.GetValue() / 3600
            time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
            
            stationPoints = np.zeros((len(elevation), len(azimuth)))

            filePath = self.satelliteFilePicker.GetPath()

            ionoParams = readIono( filePath )
            
            for elev in range(len(elevation)):
                for azim in range(len(azimuth)):
                    stationPoints[elev][azim] = iono(latitude, longitude, azimuth[azim], elevation[elev], time, ionoParams[0])
            
            x,y = np.meshgrid(azimuth, elevation)
           

           
        else:
            elevation = self.elevDegControl.GetValue() + self.elevMinControl.GetValue() / 60 + self.elevSSControl.GetValue() / 3600
            azimuth = self.azDegControl.GetValue() + self.azMinControl.GetValue() / 60 + self.azSSControl.GetValue() / 3600
            longitude = np.linspace(-180, 180, 721) 
            latitude = np.linspace(-90, 90, 361) 
            time = self.timeHHControl.GetValue() * 60 * 60 + self.timeMMControl.GetValue() * 60 + self.timeSSControl.GetValue()
            
            stationPoints = np.zeros((len(latitude), len(longitude)))

            filePath = self.satelliteFilePicker.GetPath()

            ionoParams = readIono( filePath )
            
            for lat in range(len(latitude)):
                for longit in range(len(longitude)):
                    stationPoints[lat][longit] = iono(latitude[lat], longitude[longit], azimuth, elevation, time, ionoParams[0])
            
            x,y = np.meshgrid(longitude, latitude)
            
            
        OutputNoteBookPanel.DrawCanvas(self, x, y, stationPoints)

        fig1, ax2 = plt.subplots(constrained_layout=False)
    
        CS = ax2.contourf(x, y, stationPoints, 10, cmap=plt.cm.bone)

        
        ax2.set_title('Ionospheric delay at time = {} : {} : {} '.format( self.timeHHControl.GetValue(), self.timeMMControl.GetValue(), self.timeSSControl.GetValue()))
       
        

        if self.choiceComboBox.GetValue() == 'Station analysis':
            ax2.set_xlabel('Azimuth (\u00B0)')
            ax2.set_ylabel('Elevation (\u00B0)')
        else:
            ax2.set_xlabel('Longitude (\u00B0)')
            ax2.set_ylabel('Latitude (\u00B0)')
            ax2.set_xlim([-180, 180])
            ax2.set_ylim([-90, 90])

        cbar = plt.colorbar(CS)
  
        
        maaap = plt.show()
        # DF(plt)




        

    def OnCombo (self, event):
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
        
class PreProcessingNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        b = wx.Button(self, -1, "Create and Show a ProgressDialog", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

        # Create the sizer
        noteVBookSizer = wx.BoxSizer( wx.VERTICAL )
        hSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        # The run button, needed to start processing
        self.runButton = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0 )
        hSizer.Add( self.runButton, 0, wx.ALIGN_BOTTOM|wx.ALL, 5 )

        # Show output button, needed to display output to the output AddPage
        self.showOutputButton = wx.Button( self, wx.ID_ANY, u"Show Output", wx.DefaultPosition, wx.DefaultSize, 0 )
        hSizer.Add( self.showOutputButton, 0, wx.ALIGN_BOTTOM|wx.ALL, 5 )

        # Only show the button after the processing has been done
        self.showOutputButton.Hide()        

        noteVBookSizer.Add( hSizer, 1, wx.EXPAND, 5 )
        

        self.SetSizer( noteVBookSizer )
        self.Layout()
        
        # Connect Events
        self.showOutputButton.Bind( wx.EVT_BUTTON, self.showOutput )
        self.runButton.Bind( wx.EVT_BUTTON, self.runProcessing )
        
  
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def runProcessing( self, event ):
        print('dfadfafd')
        event.Skip()

    def showOutput( self, event ):
        event.Skip()


# -------------------------------------------------------------------------------
        b = wx.Button(self, -1, "Create and Show a ProgressDialog", (50,50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)


    def OnButton(self, evt):
        max = 80

        dlg = wx.ProgressDialog("Progress dialog example",
                               "An informative message",
                               maximum = max,
                               parent=self,
                               style = 0
                                | wx.PD_APP_MODAL
                                | wx.PD_CAN_ABORT
                                # | wx.PD_CAN_SKIP
                                #| wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                | wx.PD_REMAINING_TIME
                                #| wx.PD_AUTO_HIDE
                                )

        keepGoing = True
        count = 0

        while keepGoing and count < max:
            count += 1
            wx.MilliSleep(250)
            wx.Yield()

            if count >= max / 2:
                (keepGoing, skip) = dlg.Update(count, "Half-time!")
            else:
                (keepGoing, skip) = dlg.Update(count)


        dlg.Destroy()

class OutputNoteBookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
     
        # figure=Figure()
        # axes=figure.add_subplot(111)
        # canvas=FigureCanvas(self, -1, figure)
        # axes.stock_img()
        #ax = plt.axes(projection=ccrs.PlateCarree())
        #ax.stock_img()
        #plt.plot(satelliteOrbit.sv_long, satelliteOrbit.sv_lat, 'r', transform=ccrs.Geodetic());
        #plt.show()
       

    def DrawCanvas(self, x, y, stationPoints):
        pass
        # self.panel.CreateStatusBar()

        # Add the Canvas
#         FloatCanvas.FloatCanvas.ScaleWorldToPixel = ScaleWorldToPixel
#         NC = NavCanvas.NavCanvas(self,-1,
#                                      size = (500,500),
#                                      BackgroundColor = "DARK SLATE BLUE",
#                                      ProjectionFun = YScaleFun,
#                                      )

#         self.Canvas = Canvas = NC.Canvas
#         #self.Canvas.ScaleWorldToPixel = ScaleWorldToPixel

#         self.Canvas.Bind(FloatCanvas.EVT_MOTION, self.OnMove)

#         self.Values = random.randint(0, MaxValue, (NumChannels,))

#         self.Bars = []
#         self.BarWidth = 0.75
#         # add an X axis
#         Canvas.AddLine(((0,0), (NumChannels, 0 )),)
#         for x in N.linspace(1, NumChannels, 11):
#             Canvas.AddText("%i"%x, (x-1+self.BarWidth/2,0), Position="tc")

#         for i, Value in enumerate(self.Values):
#             bar = Canvas.AddRectangle(XY=(i, 0),
#                                       WH=(self.BarWidth, Value),
#                                       LineColor = None,
#                                       LineStyle = "Solid",
#                                       LineWidth    = 1,
#                                       FillColor    = "Red",
#                                       FillStyle    = "Solid",
#                                       )
#             self.Bars.append(bar)

#         # Add a couple a button the Toolbar

#         tb = NC.ToolBar
#         tb.AddSeparator()

#         ResetButton = wx.Button(tb, label="Reset")
#         tb.AddControl(ResetButton)
#         ResetButton.Bind(wx.EVT_BUTTON, self.ResetData)

# #        PlayButton = wx.Button(tb, wx.ID_ANY, "Run")
# #        tb.AddControl(PlayButton)
# #        PlayButton.Bind(wx.EVT_BUTTON, self.RunTest)
#         tb.Realize()

#         self.Show()
#         Canvas.ZoomToBB()
#         Canvas.Draw(True)
        



###########################################################################
## RUN THE MODEL
###########################################################################

# check that the module is being run as a program and imported   
if __name__ == '__main__':
    app = wx.App()
    # The main frame object is created after creating the application object as the app is needed for the frame to execute
    frame = MainFrame(wx.Frame(None, -1, 'GNSS Data Processing'))
    frame.Show()
    #frame.Maximize(True)        # Maximize the window on first load
    app.MainLoop()
  



# ----------------------------------------------------------------------------------------------------------
# def OnOpen(self, event):

#     if self.contentNotSaved:
#         if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm",
#                          wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
#             return

#     # otherwise ask the user what new file to open
#     with wx.FileDialog(self, "Open XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
#                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

#         if fileDialog.ShowModal() == wx.ID_CANCEL:
#             return     # the user changed their mind

#         # Proceed loading the file chosen by the user
#         pathname = fileDialog.GetPath()
#         try:
#             with open(pathname, 'r') as file:
#                 self.doLoadDataOrWhatever(file)
#         except IOError:
#             wx.LogError("Cannot open file '%s'." % newfile)
# The typical usage for the save file dialog is instead somewhat simpler:

# def OnSaveAs(self, event):

#     with wx.FileDialog(self, "Save XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
#                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

#         if fileDialog.ShowModal() == wx.ID_CANCEL:
#             return     # the user changed their mind

#         # save the current contents in the file
#         pathname = fileDialog.GetPath()
#         try:
#             with open(pathname, 'w') as file:
#                 self.doSaveData(file)
#         except IOError:
#             wx.LogError("Cannot save current data in file '%s'." % pathname)


# def OnSave (self, event):
#     if not self.filename:
#         self.OnSaveAs(event)
#     else:
#         self.SaveFile()

# def OnSaveAs (self, event):
#     file = wx.FileDialog(self, message = "Save file", defaultDir = os.getcwd(), defaultFile="", wildcard=self.wildcard, style= wx.FD_SAVE | wx.FD_FILE_MUST_EXIST| wx.FD_OVERWRITE_PROMPT)
#         if file.ShowModal() == wx.ID_OK:
#             self.filename = file.GetPath()
#             if not os.path.splitext(self.filename)[1]:
#                 self.filename = filename + '.rnx'
#             self.filename = filename
#             self.SaveFile()
#             self.SetTitle(self.title + '--' + self.filename)
#         file.Destroy()