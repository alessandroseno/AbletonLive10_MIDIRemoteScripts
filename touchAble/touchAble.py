# LMH
from __future__ import with_statement

"""
# Copyright (C) 2007 Nathan Ramella (nar@remix.net)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Nathan Ramella <nar@remix.net> or visit http://www.remix.net
# 
# Additional touchAble development:
# (c) 2014 Sigabort, Lee Huddleston, ZeroConfig; admin@sigabort.co, http://sigabort.co

This script is based off the Ableton Live supplied MIDI Remote Scripts, customised
for OSC request delivery and response. This script can be run without any extra
Python libraries out of the box. 

This is the second file that is loaded, by way of being instantiated through
__init__.py

"""

import Live
#import aifc
#import wave
import struct
import touchAbleCallbacks
import RemixNet
#import os.path
import OSC
import LiveUtils
import time
import unicodedata
from threading import Timer

from collections import defaultdict
from Logger import Logger

# LMH
from _Framework.ControlSurface import ControlSurface
from SessionComponent import TouchableSessionComponent

def repr3(input_str):
    try:
        output_st = unicodedata.normalize('NFKD', input_str).encode('ascii','ignore')
        if output_st != None:
            return output_st
        else:
            return ''
    except:
        x = repr(input_str)
        return x[2:-1]


def cut_string(input_str):
    
    info = (input_str[:331] + '..') if len(input_str) > 333 else input_str
    return (info)


class touchAble(ControlSurface):
    __module__ = __name__
    __doc__ = "Main class that establishes the touchAble Component"
    
    # Enable Logging
    _LOG = 0
    
    oldloop_start = {}
    oldloop_end = {}
    oldplay_start = {}
    oldplay_end = {}
    loop_length = {}
    trackid = {}
    clipid = {}
    oldlooping  = {}
    hotlooping = {}
    
    prlisten = defaultdict(dict)
    parameters_listeners = defaultdict(dict)
    
    chainslisten = defaultdict(dict)
    chaindevicelisten = defaultdict(dict)

    plisten = {}
    device_name_listen = defaultdict(dict)
    dlisten = {}
    clisten = {}
    slisten = {}
    sslisten = {}
    sclisten = {}
    snlisten = {}
    stlisten = {}
    pplisten = {}
    cnlisten = {}
    devices_listen = {}
    drum_pad_listen = defaultdict(dict)
    drum_pads_listen = {}
    clipstartlisten = {}
    clipendlisten = {}
    cliplooplisten = {}
    noteBuffers = defaultdict(list)


    cclisten = {}
    ablisten = {}
    Rablisten = {}
    mlisten = { "solo": {}, "mute": {}, "arm": {}, "current_monitoring_state": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "color": {} }
    rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {} }
    masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }
    scenelisten = {}
    scene = 0
    track = 0
    width = 16
    offsetx = 0
    metermode = 1
    isCheckingLoop = 0
    viewwidth = 8
    updateTime = 0
    onetap = 0
    script_version = 310

    
    noteListeners = {}

    def __init__(self, c_instance):
        self._touchAble__c_instance = c_instance
        self._device_selection_follows_track_selection = True
        # LMH  
        ControlSurface.__init__( self, c_instance )
      
        self.basicAPI = 0       
        self.oscServer = RemixNet.OSCServer(self, '127.0.0.1', 9111, None, 9008)
        self.callbackManager = self.oscServer.callbackManager
        self.callbackManager.add(self.offsetxCB, "/offsetx")
        self.callbackManager.add(self.onetapCB, "/onetap")
        self.callbackManager.add(self.meterModeCB, "/metermode")
        self.callbackManager.add(self.positionsCB, "/positions")
        
        self.callbackManager.add(self.getVersion, "/getVersion")
        self.callbackManager.add(self.keepLoop, "/keepLoop")
        self.callbackManager.add(self.clearHiddenLoops, "/clearLoops")
        self.callbackManager.add(self.getActiveLoops, "/getLoops")
        self.callbackManager.add(self.changeLoopCB, "/loopChange")
        self.callbackManager.add(self.jumpForwardCB, "/jumpForward")
        self.callbackManager.add(self.jumpBackwardCB, "/jumpBackward")
        self.callbackManager.add(self.jumpLoopForward, "/jumpLoopForward")
        self.callbackManager.add(self.jumpLoopBackward, "/jumpLoopBackward")
        self.callbackManager.add(self.clip_loopstats2, "/get/clip/loopstats")
        self.callbackManager.add(self.request_loop_data, "/clip/request_loop_data")
        
        self.callbackManager.add(self.deviceLoad, "/browser/load/device")
        self.callbackManager.add(self.chainLoad, "/browser/load/chain")

        self.callbackManager.add(self.expand_device, "/expand_device")


        self.callbackManager.add(self.trackLoad, "/browser/load/track")
        self.callbackManager.add(self.returnLoad, "/browser/load/return")
        self.callbackManager.add(self.masterLoad, "/browser/load/master")
        
        self.callbackManager.add(self.clipLoad, "/browser/load/clip")
        self.callbackManager.add(self.drumpadLoad, "/browser/load/drum_pad")
        self.callbackManager.add(self.drumpadAudioEffectLoad, "/browser/load/drum_pad_audio_effect")

        self.callbackManager.add(self.getStatus, "/script/ping")
        
        self.callbackManager.add(self.clipSelected, "/clip/clip_selected")
        self.callbackManager.add(self.backFromClip, "/clip/clip_deselected")
        self.callbackManager.add(self.setClipNotes, "/clip/set_notes")
        self.callbackManager.add(self.setNoteVelocity, "/clip/set_note_velocity")
        self.callbackManager.add(self.addNote, "/clip/add_note2")
        self.callbackManager.add(self.addNotes, "/clip/add_notes2")
        self.callbackManager.add(self.updateNote, "/clip/update_note")
        self.callbackManager.add(self.removeNote, "/clip/remove_note")
        self.callbackManager.add(self.removeNotes, "/clip/remove_notes")
        self.callbackManager.add(self.stretchNotes, "/clip/stretch_notes")
        self.callbackManager.add(self.getBrowserRoot, "/browser/get_root_items")
        self.callbackManager.add(self.clearNoteBuffer, "/clip/clear_notes")
        self.callbackManager.add(self.addNotesToBuffer, "/clip/add_notes")
        self.callbackManager.add(self.replaceCurrentNotesWithBuffer, "/clip/replace_notes")
        
        self.callbackManager.add(self.session_record_chang, "/live/set/session_record")
        self.callbackManager.add(self.session_record_status_chang, "/live/set/trigger_session_record")
        self.callbackManager.add(self.re_enable_automation_enabled_chang, "/live/set/re_enable_automation")
        self.callbackManager.add(self.session_automation_record_chang, "/live/set/session_automation_record")
        self.callbackManager.add(self.broadcast, "/broadcast")
        
        self.callbackManager.add(self.sesion_capture_midi, "/live/set/capture_midi")


        #self.oscServer.sendOSC('/remix/oscserver/startup', 1)
        self.logger = self._LOG and Logger() or 0
        self.log("Logging Enabled")
        self.mlcache = []
        self.mrcache = [] 
        self.mmcache = 0

        # LMH
        with self.component_guard():
            self._create_session()
        
        # listener
        self.update_all_listeners()
        
    
        self.mlcache = [-1 for i in range(2000)]
        self.mrcache = [-1 for i in range(2000)]
        self.mmcache = -1


    # LMH
    def _log( self, msg, force = False ):
        if self._LOG or force:
            self.log_message( msg )
            
    def _create_session(self):
        log_text = "_create_session : v " + str(self.script_version)
        self._log( log_text , True )
        self.session = TouchableSessionComponent(touchAble = self, name = 'Session', num_tracks = 1, num_scenes = 1, is_enabled=True, auto_name=True, enable_skinning=True)
        self.session.set_show_highlight( True )

        self._send_lsync_coords()
        self._log( "_create_session complete", True )
        
    def set_lsync_offsets(self,x,y,w,h):
        self._log( "set_lsync_offsets: " + str( x ) + ", " + str( y ) + ", " + str( w ) + ", " + str( h ) )
        self.session._set_lsync_offsets( x, y, w, h )
    
    def broadcast( self, msg ):
        self.session._broadcast( msg )
    
    def _send_lsync_coords(self):
        self._log( "_send_lsync_coords" )
        self.session._send_lsync_coords( "6" )
        
    #self.log(str(Live.Application.get_application().view.available_main_views()))
        #self.song().master_track.create_device(str("EQEight"))
    

    
    def getBrowserRoot(self, msg):

        browser = self.application().browser

        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)

        steps = 1
        i = 0
        indices = []

        self.oscServer.sendOSC("/bundle/start", 1)
        self.oscServer.sendOSC("/browser/start", 1)


        for item in root_items:

            lis = list(indices)

            self.getChildren(item, steps, lis, i)

            i = i+1

        
        self.oscServer.sendOSC("/browser/end", 1)
        self.oscServer.sendOSC("/finish_loading", (1))
        self.oscServer.sendOSC("/bundle/end", 1)




    def getChildren(self, item, steps, indices, i):
        is_folder = 0
        if len(item.children)>0:
            is_folder = 1
        else:
            pass
        count = len(item.children)
        
        indices.append(int(i))
        indis = [repr3(item.name), int(steps), int(item.is_loadable), int(count)]
        for index in indices:
            indis.append(int(index))
        j = 0
        self.oscServer.sendOSC("/browser/item", tuple(indis))
        steps = steps+1

        if is_folder == 1:
            for subItem in item.children:

                lis = list(indices)
                self.getChildren(subItem, steps, lis, j)
                j = j+1
        else:
            pass


    def deviceLoad(self, msg):
        position = msg[2]
        type = msg[3]
        tid = msg[4]
        steps = msg[5]
        #self.oscServer.sendOSC("/browser/loadstart", 1)

        track = self.song().master_track
        if type == 0:
            track = self.song().tracks[tid]
        elif type == 2:
            track = self.song().return_tracks[tid]

        self.song().view.selected_track = track
        browser = self.application().browser
        
        #self.oscServer.sendOSC("/browser/loadstart", 2)

        if position == 1:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_left
        elif position == 0:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
        elif position == -1:
            track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
        #self.oscServer.sendOSC("/browser/loadstart", 3)

        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        
        item = root_items[msg[6]]
        #self.oscServer.sendOSC("/browser/loadstart", 4)

        for i in range(steps-1):
            
            index = msg[7+i]
            item = item.children[index]
        
        browser.load_item(item)


    def chainLoad(self, msg):
        type = msg[2]
        tid = msg[3]
        steps = msg[4]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = self.song().master_track
        if type == 0:
            track = self.song().tracks[tid]
        elif type == 2:
            track = self.song().return_tracks[tid]
    
        #self.song().view.selected_track = track
        browser = self.application().browser
        
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        track.view.device_insert_mode = Live.Track.DeviceInsertMode.default
        #self.oscServer.sendOSC("/browser/loadstart", 3)
    

        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[5]]
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        for i in range(steps-1):
            
            index = msg[6+i]
            item = item.children[index]
        
            
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        if not self.application().view.browse_mode:
            self.application().view.toggle_browse()

        browser.load_item(item)
        
        browser.hotswap_target = None


        if self.application().view.browse_mode:
            self.application().view.toggle_browse()

        #self.oscServer.sendOSC("/browser/loadstart", 6)






    def trackLoad(self, msg):
        trk = msg[2]
        steps = msg[3]
        #self.oscServer.sendOSC("/browser/loadstart", 1)

        track = self.song().tracks[trk]
        application = self.application()
        
        self.song().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")

        browser = self.application().browser
        
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[4]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)

        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)

            index = msg[5+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)

        #if not Live.Application.get_application().view.browse_mode:
            #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)

        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
                
        #if Live.Application.get_application().view.browse_mode:
            #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    def returnLoad(self, msg):
        trk = msg[2]
        steps = msg[3]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = self.song().return_tracks[trk]
        application = self.application()
        
        self.song().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = self.application().browser
        
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[4]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)
            
            index = msg[5+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)
        
        #if not Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        #if Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    
    def masterLoad(self, msg):
        steps = msg[2]
        self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = self.song().master_track
        application = self.application()
        
        self.song().view.selected_track = track
        
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = self.application().browser
        
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[3]]
        #self.oscServer.sendOSC("/browser/loadstart", 2)
        
        for i in range(steps-1):
            #self.oscServer.sendOSC("/browser/loadstart", 3)
            
            index = msg[4+i]
            item = item.children[index]
        #self.oscServer.sendOSC("/browser/loadstart", 3)
        
        #if not Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        #self.oscServer.sendOSC("/browser/loadstart", 4)
        
        browser.load_item(item)
        #self.oscServer.sendOSC("/browser/loadstart", 5)
        
        #if Live.Application.get_application().view.browse_mode:
        #Live.Application.get_application().view.toggle_browse()
        self.oscServer.sendOSC("/browser/loadstart", 6)

    def get_device_for_message(self,msg):
    
        type = msg[2]
        tid = msg[3]
        did = msg[4]
    
        number_of_steps = msg[5]
        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track

        device = track.devices[did]

        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
    
            track = device.chains[chain_id]
            device = track.devices[device_id]

        return device


    def drumpadLoad(self, msg):
        #self.oscServer.sendOSC("/browser/load/drumpad", 1)
        trk = msg[2]
        dev = msg[3]
        
        number_of_steps = msg[4]
        
        track = self.song().tracks[trk]
        trackk = track;
        device = track.devices[dev]
        
        for i in range(number_of_steps):
            chain_id = msg[5+i*2]
            device_id = msg[6+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]

        
        pad = 127-msg[5 + number_of_steps * 2]

        steps = msg[6 + number_of_steps * 2]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        
        browser = self.application().browser


        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[7 + number_of_steps * 2]]
        
        for i in range(steps-1):
            
            index = msg[8 + number_of_steps * 2 +i]
            item = item.children[index]
        
        drum_pad = device.drum_pads[pad]
                    
                

            
        self.song().view.selected_track = trackk
        #self.song().view.select_device(device)
        self.application().view.show_view("Detail/DeviceChain")
            
        if isinstance(drum_pad, Live.DrumPad.DrumPad):
            if drum_pad.chains and drum_pad.chains[0].devices:
                self.song().view.select_device(drum_pad.chains[0].devices[0])
                drum_pad.canonical_parent.view.selected_chain = drum_pad.chains[0]
                browser.hotswap_target = drum_pad.chains[0]

            else:
                browser.hotswap_target = drum_pad

            
            drum_pad.canonical_parent.view.selected_drum_pad = drum_pad

            
            #self.oscServer.sendOSC("/browser/loadstart", 2)

            #browser.hotswap_target = drum_pad
                
            if not self.application().view.browse_mode:
                self.application().view.toggle_browse()

            browser.load_item(item)

            if self.application().view.browse_mode:
                self.application().view.toggle_browse()

        else:
            pass
   
        #self.oscServer.sendOSC("/browser/loadstart", 6)
    
    
    def drumpadAudioEffectLoad(self, msg):
        #self.oscServer.sendOSC("/browser/load/drumpad", 1)

        trk = msg[2]
        dev = msg[3]
        
        number_of_steps = msg[4]
        
        track = self.song().tracks[trk]
        device = track.devices[dev]
        
        for i in range(number_of_steps):
            chain_id = msg[5+i*2]
            device_id = msg[6+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]
        
        pad = 127-msg[5 + number_of_steps * 2]
        
        steps = msg[6 + number_of_steps * 2]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        
        track = self.song().tracks[trk]
        device = track.devices[dev]
        
        
        browser = self.application().browser
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)
        
        item = root_items[msg[7 + number_of_steps * 2]]
        
        for i in range(steps-1):
            
            index = msg[8 + number_of_steps * 2+i]
            item = item.children[index]
        
        drum_pad = device.drum_pads[pad]
        
        
        
        
        self.song().view.selected_track = track
        #self.song().view.select_device(device)
        self.application().view.show_view("Detail/DeviceChain")
        
        if isinstance(drum_pad, Live.DrumPad.DrumPad):
            if drum_pad.chains and drum_pad.chains[0].devices:
                self.song().view.select_device(drum_pad.chains[0].devices[0])
                drum_pad.canonical_parent.view.selected_chain = drum_pad.chains[0]
                browser.hotswap_target = drum_pad.chains[0]
                #self.oscServer.sendOSC("/browser/loadstart", 2)

            else:
                browser.hotswap_target = drum_pad
                #self.oscServer.sendOSC("/browser/loadstart", 3)


            #self.oscServer.sendOSC("/browser/loadstart", 4)

            
            
            drum_pad.canonical_parent.view.selected_drum_pad = drum_pad
            
            
            #self.oscServer.sendOSC("/browser/loadstart", 5)
            
            #browser.hotswap_target = drum_pad
            
            if not self.application().view.browse_mode:
                self.application().view.toggle_browse()
                
            browser.load_item(item)

            if self.application().view.browse_mode:
                self.application().view.toggle_browse()
                
            
        
        #self.oscServer.sendOSC("/browser/loadstart", 6)

    def clipLoad(self, msg):
        trk = msg[2]
        scene = msg[3]
        steps = msg[4]
        #self.oscServer.sendOSC("/browser/loadstart", 1)
        message = "track: " + str(trk) + "scene: " + str(scene)
        self.oscServer.sendOSC("/NSLOG_REPLACE", message)

        track = self.song().tracks[trk]
        ascene = self.song().scenes[scene]

        clip_slot = track.clip_slots[scene]
        
        """ self.song().view.highlighted_clip_slot = clip_slot """
        

        self.song().view.selected_track = track
        self.song().view.selected_scene = ascene
        
        self.oscServer.sendOSC("/NSLOG_REPLACE", message)

        self.application().view.show_view("Detail/Clip")
                
        #Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
        browser = self.application().browser
        
        root_items = []
        root_items.append(browser.sounds)
        root_items.append(browser.drums)
        root_items.append(browser.instruments)
        root_items.append(browser.audio_effects)
        root_items.append(browser.midi_effects)
        root_items.append(browser.max_for_live)
        root_items.append(browser.plugins)
        root_items.append(browser.clips)
        root_items.append(browser.samples)
        root_items.append(browser.packs)
        root_items.append(browser.user_library)

        self.oscServer.sendOSC("/NSLOG_REPLACE", "2")

        item = root_items[msg[5]]
        
        for i in range(steps-1):
            index = msg[6+i]
            item = item.children[index]

        self.oscServer.sendOSC("/NSLOG_REPLACE", "load item")

        self.song().view.selected_track = track
        self.song().view.selected_scene = ascene

    
        browser.load_item(item)

        self.oscServer.sendOSC("/NSLOG_REPLACE", "2")

            

    def onetapCB(self, msg):
        self.onetap = msg[2]
    
    def clipSelected(self, msg):

        track = msg[2]
        scene = msg[3]
        length = msg[4]
        trk = self.song().tracks[track]
        clip = trk.clip_slots[scene].clip
        
        
        
        if clip == None:
            a = Live.Application.get_application().get_major_version()
            if a >= 9:
                clipSlot = self.song().tracks[track].clip_slots[scene]
                clipSlot.create_clip(float(length))
                clip = clipSlot.clip
                if clip.name != None:
                    nm = cut_string(clip.name)
                else:
                    nm = " "
                self.oscServer.sendOSC("/clip", (track, scene, repr3(nm), clip.color, 0))

            else:
                pass



        key = '%s.%s' % (track, scene)

        cb = lambda :self.notesChanged(track, scene, key)
        if self.noteListeners.has_key(key) != 1:
            clip.add_notes_listener(cb)
            self.noteListeners[key] = cb

        clip = self.song().tracks[track].clip_slots[scene].clip
                    
        self.song().view.selected_track = trk
        self.song().view.detail_clip = clip
        Live.Application.get_application().view.show_view("Detail/Clip")

        
        notes = [int(track)]
        notes.append(int(scene))
        count = 0
        
        clip.select_all_notes()
        
        clipNotes = clip.get_selected_notes()
        clip.deselect_all_notes()
        loopstart = 0
        looplength = 0
        start = 0
        end = 0
        looping = clip.looping
        
        if looping == 1:
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            
            clip.looping = 0            
            start = clip.loop_start
            end = clip.loop_end
            clip.looping = 1
        
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            clip.looping = 0
                    
        try:
            start = clip.start_marker
            end = clip.end_marker
        except:
            pass
        #self.oscServer.sendOSC("/bundle/start", (1))

        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))

        self.oscServer.sendOSC("/clip/start_receiving_notes", 1)
        
        noteBuffer = self.noteBuffers[key]

                
        for note in clipNotes:
            noteBuffer.append(note)
            for var in note:
                notes.append(float(var))
            count = count+1
            if count == 128:
                self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
                count = 0
                notes = [int(track)]
                notes.append(int(scene))
        
        self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
        self.oscServer.sendOSC("/clip/end_receiving_notes", 1)
        self.oscServer.sendOSC("/finish_loading", (1))
        #self.oscServer.sendOSC("/bundle/end", (1))


    def update_listeners_for_device(self, device, track, tid, did, type, num, number_of_steps, lis, device_id):


        self.add_device_listeners_for_track(track, int(tid), int(type))



        self.send_update_for_device(device, track, int(tid), int(did), int(type), int(num), int(number_of_steps), lis, int(device_id))


    def expand_device(self, msg):

        type = msg[2]
        tid = msg[3]
        did = msg[4]
        
        number_of_steps = msg[5]
        
        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        
        device = track.devices[did]
        num = len(track.devices)
        indices = []
        device_id = -1
        

        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            num = len(chain.devices)
            
            indices.append(int(device_id))
        
        self.oscServer.sendOSC("/NSLOG_REPLACE", repr3(device.class_name))


        if device.class_name == 'OriginalSimpler':

            simpler = device

            for parameter in device.parameters:
                
                if parameter.name == 'Pe On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'L On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'Fe On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                elif parameter.name == 'F On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                else:
                    pass
          

        elif device.class_name == 'MultiSampler':
        
            for parameter in device.parameters:
                
                
                if parameter.name == 'Osc On':
                    
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'Pe On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                
                elif parameter.name == 'Shaper On':
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value

                elif parameter.name == 'L 1 On':
                    
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'L 2 On':
                    
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'L 3 On':
                    
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'Ae On':
                    
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'F On':
                            
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                elif parameter.name == 'Fe On':
                            
                    old_value = parameter.value
                    parameter.value = 1
                    parameter.value = old_value
                
                else:
                    pass
            
    

    def clearNoteBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = self.song().tracks[track].clip_slots[scene].clip

        key = '%s.%s' % (track, scene)
        self.noteBuffers[key] = []
            


    
    def addNotesToBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        noteCount = (len(msg)-4)/5
        key = '%s.%s' % (track, scene)

        
        noteBuffer = self.noteBuffers[key]

            
        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = msg[(ind+0)]
            time = msg[(ind+1)]
            length = msg[(ind+2)]
            velocity = msg[(ind+3)]
            mute = msg[(ind+4)]
            
            noteDescription.append(int(pitch))
            noteDescription.append(float(time))
            noteDescription.append(float(length))
            noteDescription.append(float(velocity))
            noteDescription.append(bool(mute))
            
            noteBuffer.append(noteDescription)
            


    def replaceCurrentNotesWithBuffer(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = self.song().tracks[track].clip_slots[scene].clip
        clip.select_all_notes()
        key = '%s.%s' % (track, scene)
                    
        noteBuffer = self.noteBuffers[key]

       
        clip.replace_selected_notes(tuple(noteBuffer))
        clip.deselect_all_notes()
            
                
    
    def setClipNotes(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = self.song().tracks[track].clip_slots[scene].clip
        
        clip.select_all_notes()
        newClipNotes = []
        
        noteCount = (len(msg)-4)/5

        newNotes = []
        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = msg[(ind+0)]
            time = msg[(ind+1)]
            length = msg[(ind+2)]
            velocity = msg[(ind+3)]
            mute = msg[(ind+4)]

            noteDescription.append(int(pitch))
            noteDescription.append(float(time))
            noteDescription.append(float(length))
            noteDescription.append(float(velocity))
            noteDescription.append(bool(mute))            

            newClipNotes.append(noteDescription)

            
        clip.replace_selected_notes(tuple(newClipNotes))
        clip.deselect_all_notes()


    def setNoteVelocity(self, msg):

        track = msg[2]
        scene = msg[3]

        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
        
        clip = self.song().tracks[track].clip_slots[scene].clip
        
        #clip.remove_notes(time, pitch, length, 1)
        
        newClipNotes = []
        noteDescription = []

        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))


            
    def addNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
       
        clip = self.song().tracks[track].clip_slots[scene].clip
                
        newClipNotes = []
        noteDescription = []
        
        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))
    
    
    def addNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        noteCount = (len(msg)-4)/5
        
        newClipNotes = []

        for i in range(noteCount):
            noteDescription = []
            ind = 4 + (i*5)
            pitch = int(msg[(ind+0)])
            time = float(msg[(ind+1)])
            length = float(msg[(ind+2)])
            velocity = float(msg[(ind+3)])
            mute = bool(msg[(ind+4)])
        
            noteDescription.append(pitch)
            noteDescription.append(time)
            noteDescription.append(length)
            noteDescription.append(velocity)
            noteDescription.append(mute)
        
            newClipNotes.append(noteDescription)
        
        clip = self.song().tracks[track].clip_slots[scene].clip
        clip.set_notes(tuple(newClipNotes))

    def updateNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        velocity = float(msg[7])
        mute = bool(msg[8])
        
        oldpitch = int(msg[9])
        oldtime = float(msg[10])
        oldlength = float(msg[11])
        
        clip = self.song().tracks[track].clip_slots[scene].clip
        
        clip.remove_notes(oldtime - 0.001, oldpitch, oldlength - 0.002, 1)
        
        newClipNotes = []
        noteDescription = []
        
        noteDescription.append(pitch)
        noteDescription.append(time)
        noteDescription.append(length)
        noteDescription.append(velocity)
        noteDescription.append(mute)
        
        newClipNotes.append(noteDescription)
        clip.set_notes(tuple(newClipNotes))

    
    
    def removeNote(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        
        clip = self.song().tracks[track].clip_slots[scene].clip
        clip.remove_notes(time - 0.001, pitch, length - 0.002, 1)
    
    def removeNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        
        pitch = int(msg[4])
        time = float(msg[5])
        length = float(msg[6])
        
        clip = self.song().tracks[track].clip_slots[scene].clip
        clip.remove_notes(time - 0.001, pitch, length - 0.002, 1)
    
    
    
    def stretchNotes(self, msg):
        
        track = msg[2]
        scene = msg[3]
        factor = msg[4]
        clip = self.song().tracks[track].clip_slots[scene].clip

        clipLength = 0
        looping = 0
        if clip.looping:
            clip.looping = 0

            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            
            clip.looping = 1
            looping = 1
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start

        else:
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            
            clip.looping = 1
            clip.loop_end = (clip.loop_end-clip.loop_start)*factor + clip.loop_start
            clip.looping = 0
    

        
        clip.select_all_notes()
        notes = clip.get_selected_notes()


        newClipNotes = []
        
        for note in notes:
            noteDescription = []

            pitch = int(note[0])
            time = float(note[1])
            length = float(note[2])
            velocity = float(note[3])
            mute = bool(note[4])


            length = length*factor
            time = time*factor
            
            noteDescription.append(pitch)
            noteDescription.append(time)
            noteDescription.append(length)
            noteDescription.append(velocity)
            noteDescription.append(mute)
        
            newClipNotes.append(noteDescription)

    
        clip.replace_selected_notes(tuple(newClipNotes))
    
        
        is_audio_clip = int(0)
        warp = 0
        start = 0
        end = 0
        loop_start = 0
        loop_end = 0;
            

        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            
            clip.looping = int(0)
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end

        if looping == 1:
            clip.looping = 1
        else:
            clip.looping = 0

        self.oscServer.sendOSC("/clip/loopstats", (int(track), int(scene), looping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))

    

    def notesChanged(self, track, scene, clip):
        notes = [int(track)]
        notes.append(int(scene))
        count = 0
        clip = self.song().tracks[int(track)].clip_slots[int(scene)].clip
        a = Live.Application.get_application().get_major_version()
        clipNotes = []

        #if a >= 9:
        #clipNotes = clip.get_notes(float(0), int(0), float(clip.end_marker-clip.start_marker), int(127))
        #else:
        clip.select_all_notes()
        clipNotes = clip.get_selected_notes()
        clip.deselect_all_notes()
                
        loopstart = 0
        looplength = 0
        start = 0
        end = 0
        looping = 0
        loopend = 0
        version = 0
            
        
        #self.oscServer.sendOSC("/bundle/start", (1))
        if a >= 9:
            start = clip.start_marker
            end = clip.end_marker
            loopstart = clip.loop_start
            loopend = clip.loop_end
            self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))

            self.oscServer.sendOSC("/clip/start_receiving_notes", 1)

        else:
            loopstart = clip.loop_start
            loopend = clip.loop_end
            start = loopstart
            end = loopend
            self.oscServer.sendOSC("/clip/request_loop_data", (int(track), int(scene)))

            self.oscServer.sendOSC("/clip/start_receiving_notes", 1)

        key = '%s.%s' % (track, scene)

        noteBuffer = []
        self.noteBuffers[key] = noteBuffer

        for note in clipNotes:

            for var in note:
                notes.append(float(var))
            
            noteBuffer.append(note)

            count = count+1
            if count == 128:
                self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
                count = 0
                notes = [int(track)]
                notes.append(int(scene))

        self.oscServer.sendOSC("/clip/receive_notes", tuple(notes))
        self.oscServer.sendOSC("/clip/end_receiving_notes", 1)
                    
        #self.oscServer.sendOSC("/finish_loading", (1))
        #self.oscServer.sendOSC("/bundle/end", (1))



    def backFromClip(self, msg):
                
        track = msg[2]
        scene = msg[3]
        
        key = '%s.%s' % (track, scene)
        clip = self.song().tracks[track].clip_slots[scene].clip

        if clip.notes_has_listener(self.noteListeners[key]) == 1:
            clip.remove_notes_listener(self.noteListeners[key])
            del self.noteListeners[key]
       
                
        
    def request_loop_data(self, msg):
        track = msg[2]
        scene = msg[3]
        clip = self.song().tracks[int(track)].clip_slots[int(scene)].clip
        loopstart = 0
        start = 0
        end = 0
        loopend = 0
            
        looping = clip.looping
            
        if looping == 1:
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            
            clip.looping = 0
            start = clip.loop_start
            end = clip.loop_end
            clip.looping = 1
        
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            
            loopstart = clip.loop_start
            loopend = clip.loop_end
            clip.looping = 0
        
        try:
            start = clip.start_marker
            end = clip.end_marker
        except:
            pass
                
        self.oscServer.sendOSC("/clip/requested_loop_stats", (int(track), int(scene), float(start), float(end), float(loopstart), float(loopend)))


    

    def loopStartCB(self, msg):
        
        track = msg[2]
        scene = msg[3]
        self.oscServer.sendOSC("/clip/loopstart", 1)
        clip = self.song().tracks[int(track)].clip_slots[int(scene)].clip

        loopStart = msg[4]
        clip.loop_start = loopStart
        self.oscServer.sendOSC("/clip/loopstart", 2)
    
    
    def loopEndCB(self, msg):
        
        track = msg[2]
        scene = msg[3]
        self.oscServer.sendOSC("/clip/loopend", 1)

        clip = self.song().tracks[int(track)].clip_slots[int(scene)].clip

        loopEnd = msg[4]
        self.oscServer.sendOSC("/clip/loopend", 1)
        
        clip.loop_end = loopEnd
        self.oscServer.sendOSC("/clip/loopend", 2)


    def offsetxCB(self, msg):
        """Called when a /offsetx message is received.

        Messages:
        /offsetx     (offset)
        """
        self.offsetx = msg[2]
        self.oscServer.sendOSC("/offsetx", self.offsetx)
        
    def positionsCB(self, msg):
        self.positions()
        
    def meterModeCB(self, msg):

        self.metermode = msg[2]
        self.oscServer.sendOSC("/metermode", self.metermode)

    def getStatus(self, msg):   
    	# LMH
        self.session._ping( msg )
        #self.oscServer.sendOSC("/script/pong", 310)
        #self._log( "script/pong", True )
        xx = int(self.oscServer.udpServer.srcPort)
        #self._log(str(xx), True )
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        
        self.oscServer.sendOSC("/script/pong", (400, int(xx), int(a), int(b), int(c)))
    
    def getVersion(self, msg):
        
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        self.oscServer.sendOSC("/live/version", (int(a), int(b), int(c)))

    
    
    def getActiveLoops(self, msg):

        for clip in self.oldloop_start:
            if clip != None:
                tr = int(self.trackid[clip])
                cl = int(self.clipid[clip])
                ll = float(self.loop_length[clip])
                self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 1, float(ll)))
                
            
    def clearHiddenLoops(self, msg):
        for clip in self.oldloop_start:
            if clip != None:
                if clip.is_playing == 1:
                    clip.looping = 0
                    
                    clip.loop_end = float(self.oldplay_end[clip])
                    clip.loop_start = float(self.oldplay_start[clip])
                    
                    clip.looping = 1
                    
                    clip.loop_end = float(self.oldloop_end[clip])
                    clip.loop_start = float(self.oldloop_start[clip])
                    
                    if clip.loop_end > float(self.oldloop_end[clip]):
                        clip.loop_end = float(self.oldloop_end[clip])
                    else:
                        pass
                    
                    if clip.loop_end < float(self.oldloop_end[clip]):
                        clip.loop_end = float(self.oldloop_end[clip])
                    else:
                        pass
                    
                    clip.looping = int(self.oldlooping[clip])
                    
                    tr = int(self.trackid[clip])
                    cl = int(self.clipid[clip])

                    del self.oldplay_start[clip]
                    del self.oldplay_end[clip]
                    del self.oldloop_start[clip]
                    del self.oldloop_end[clip]
                    del self.oldlooping[clip]
                    del self.hotlooping[clip]
                    del self.loop_length[clip]
                    del self.trackid[clip]
                    del self.clipid[clip]
                    self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 0, float(4)))
                else:
                    pass
            else:
                pass
            
   
    
    def changeLoopCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        
        clip2 = LiveUtils.getClip(tr, cl)
        clip2.loop_end = clip2.loop_start + length
        clip2.looping = 0
        clip2.loop_end = clip2.loop_start + length
        clip2.looping = 1
        for clip in self.loop_length:
            if clip != None:
                if clip == clip2:
                    self.loop_length[clip] = float(length)
        
        self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 1, float(length)))

                    
    def clip_loopstats(self, clip, tid, cid):
        
        clip = LiveUtils.getClip(tid, cid)
        isLooping = int(clip.looping)
        self.oscServer.sendOSC('/clip/sdsd', (tid, cid))

        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            
            clip.looping = 0
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end
        
        clip.looping = isLooping
        self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end))
    

    def clip_loopstats2(self, msg):
                    
        tid = msg[2]
        cid = msg[3]
                                                
        clip = LiveUtils.getClip(tid, cid)
            
        isLooping = int(clip.looping)
        
        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
                            
            clip.looping = int(0)
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end
                            
            clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end
                        
        clip.looping = isLooping
        self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end))

    
    #self.oscServer.sendOSC('/oldLoopData', (track, clip, looping, loopStart, loopLength))

    def keepLoop(self, msg):
        tr = msg[2]
        cl = msg[3]
        clip2 = LiveUtils.getClip(tr, cl)
        for clip in self.oldloop_start:
            if clip != None:
                if clip == clip2:
                    del self.oldplay_start[clip]
                    del self.oldplay_end[clip]
                    del self.oldloop_start[clip]
                    del self.oldloop_end[clip]
                    del self.oldlooping[clip]
                    del self.hotlooping[clip]
                    del self.loop_length[clip]
                    del self.trackid[clip]
                    del self.clipid[clip]
                    self.oscServer.sendOSC('/clip/hotlooping', (int(tr), int(cl), 0, float(4)))
    
    def jumpForwardCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        
        clip.move_playing_pos(length)
    
    def jumpBackwardCB(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        
        clip.move_playing_pos(length)
    
    
    def jumpLoopForward(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        
        clip = LiveUtils.getClip(tr, cl)
        clip.looping = 1
        start = clip.loop_start
        
        clip.loop_end = clip.loop_end + length
        clip.move_playing_pos(length)
        clip.loop_start = start + length
        
        #end = clip.loop_end
        #start = clip.loop_start
        #size = end - start
        
        #clip.looping = 0
        
        
        #clip.loop_end = end
        #clip.loop_start = start

        #if end > start + length:
        #clip.loop_start = start + length
        #else:
        #clip.loop_start = end - length
        #clip.looping = 1

    
    
    
    
    def jumpLoopBackward(self, msg):
        
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
        start = clip.loop_start
        
        clip.looping = 1
        
        size = clip.loop_end - start
        
        if start+length > 0:
            clip.loop_start = start + length
            #clip.move_playing_pos(size)
            clip.loop_end = clip.loop_end + length
            #start = clip.loop_start
        else:
            clip.loop_start = 0
            clip.loop_end = size
            #start = 0
        clip.move_playing_pos(length)
                
        #end = clip.loop_end
        #start = clip.loop_start
        #clip.looping = 0
            
        #clip.loop_end = end
        #clip.loop_start = start
        #clip.looping = 1
            
            
######################################################################
# Standard Ableton Methods

    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules
        """
        return

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        """
        To be called from any components, as soon as their internal state changed in a 
        way, that we do need to remap the mappings that are processed directly by the 
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame.
        """
        return
    
    def update_display(self):
        """
        This function is run every 100ms, so we use it to initiate our Song.current_song_time
        listener to allow us to process incoming OSC commands as quickly as possible under
        the current listener scheme.
        """
        ######################################################
        # START OSC LISTENER SETUP

        if self.basicAPI == 0:
            # By default we have set basicAPI to 0 so that we can assign it after
            # initialization. We try to get the current song and if we can we'll
            # connect our basicAPI callbacks to the listener allowing us to 
            # respond to incoming OSC every 60ms.
            #
            # Since this method is called every 100ms regardless of the song time
            # changing, we use both methods for processing incoming UDP requests
            # so that from a resting state you can initiate play/clip triggering.
            
            try:
                doc = self.song()
            except:
                return
            try:
                # LMH
                self.basicAPI = touchAbleCallbacks.touchAbleCallbacks(self._touchAble__c_instance, self.oscServer, self)
                # Commented for stability
                #doc.add_current_song_time_listener(self.oscServer.processIncomingUDP)
                self.oscServer.sendOSC('/status/finished_loading', (9010))
                #self.oscServer.sendOSC("/server/refresh", (1))

                
            except:
                return
    
            
            # If our OSC server is listening, try processing incoming requests.
            # Any 'play' initiation will trigger the current_song_time listener
            # and bump updates from 100ms to 60ms.

        
        
            
        if self.oscServer:
            try:
                #self.oscServer.sendOSC('/processingOSC', (1))
                
                self.oscServer.processIncomingUDP()
        
            except:
                pass
        #self.updateTime = self.updateTime +4
        #if self.updateTime >= 100:
        if self.oscServer:
            self.positions()
            self.mastermeters()
            self.meters()
            self.songtime_change()
            #self.updateTime = 0

            
        # END OSC LISTENER SETUP
        ######################################################

    def send_midi(self, midi_event_bytes):
        """
        Use this function to send MIDI events through Live to the _real_ MIDI devices 
        that this script is assigned to.
        """
        pass

    def receive_midi(self,midi_bytes):
        #self.oscServer.sendOSC('/midi/received', (midi_bytes))
        
        if midi_bytes[0] == 240:
            if self.oscServer:
                try:
                    self.oscServer.processIncomingUDP()
                except:
                    pass
        else:
            pass
        
        
            
    def can_lock_to_devices(self):
        return True

    def suggest_input_port(self):
        return 'touchAble'

    def suggest_output_port(self):
        return ''

    def suggest_map_mode(self, cc_no, channel):
        return Live.MidiMap.MapMode.absolute
    
    def __handle_display_switch_ids(self, switch_id, value):
        pass
    
    
######################################################################
# Useful Methods


    def getOSCServer(self):
        return self.oscServer
    
    def application(self):
        """returns a reference to the application that we are running in"""
        return Live.Application.get_application()

    def song(self):
        """returns a reference to the Live Song that we do interact with"""
        return self._touchAble__c_instance.song()

    def handle(self):
        """returns a handle to the c_interface that is needed when forwarding MIDI events via the MIDI map"""
        return self._touchAble__c_instance.handle()
    def log(self, msg):
        if self._LOG == 1:
            self.logger.log(msg) 
            
    def getslots(self):
        tracks = self.song().tracks

        clipSlots = []
        for track in tracks:
            clipSlots.append(track.clip_slots)
        return clipSlots


    def positions(self):
        tracks = self.song().tracks
        pos = 0
        ps = 0
        if self.song().is_playing != 4:
            #self.oscServer.sendOSC("/bundle/start", 1)
            for i in range(len(tracks)):
                track = tracks[i]
                if track.is_foldable != 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            ps = track.playing_slot_index
                            clip = track.clip_slots[ps].clip
                            playing_pos = 0
                            pos = 0
                            try:
                                playing_pos = clip.playing_position
                                if clip.looping == 1:
                                    if clip.playing_position < clip.loop_start:
                                        #clip.looping = 0
                                        start = clip.loop_start
                                        end = clip.loop_end
                                        #clip.looping = 1
                                        pos = 1 - round((end - clip.playing_position) / end, 6)
                                            #pos = round((clip.loop_start - clip.playing_position) / (clip.loop_start - start), 3)
                                    else:
                                        pos = round((clip.playing_position - clip.loop_start) / (clip.loop_end - clip.loop_start), 6)

                                else:
                                    pos = round((clip.playing_position-clip.loop_start) / (clip.loop_end - clip.loop_start), 6)
                            except:
                                asddd = 1

                            self.oscServer.sendOSC('/clip/playing_position',(i, ps, pos, playing_pos))
                        else:
                            pass
                    else:
                        pass

                else:
                    pass
            #self.oscServer.sendOSC("/bundle/end", (1))

        else:
            pass

            


    def meters(self):
        #self.oscServer.sendOSC("/bundle/start", 1)
        tracks = self.song().tracks
        vall = 0
        valr = 0
        for i in range (len(tracks)):
            track = tracks[i]
            if track.has_audio_output:
                vall = track.output_meter_left
                valr = track.output_meter_right
            else:
                vall = 0
                valr = 0
            
            vall = round(vall, 3)
            valr = round(valr, 3)

            if vall != self.mlcache[i]:
                self.oscServer.sendOSC('/track/meter',(i,vall, valr))
                self.mlcache[i] = vall                    
            else:
                pass
        #self.oscServer.sendOSC("/bundle/end", (1))


            

    def mastermeters(self):
        tracks = self.song().return_tracks
        vall = self.song().master_track.output_meter_left
        valr = self.song().master_track.output_meter_right
        
        vall = round(vall, 2)
        valr = round(valr, 2)

        if vall != self.mmcache:
            self.oscServer.sendOSC('/master/meter',(vall, valr))
            if vall == 0:
                self.oscServer.sendOSC('/master/meter',(0.0000000001))   
            self.mmcache = vall                    
        i = 0
        for track in tracks:
            vall = track.output_meter_left
            valr = track.output_meter_right

            vall = round(vall, 2)
            valr = round(valr, 2)

            if vall != self.mrcache[i]:
                self.oscServer.sendOSC('/return/meter',(i, vall, valr))
                self.mrcache[i] = vall
            else:
                pass
            i = i+1

        

        
######################################################################
# Used Ableton Methods

    def disconnect(self):
        
        try:
            try:
                self.rem_clip_listeners()
            except:
                self.log_message("rem_clip_listeners failed")
            
            
            try:
                self.rem_mixer_listeners()
            except:
                self.log_message("rem_mixer_listeners failed")
            
            
            try:
                self.rem_scene_listeners()
            except:
                self.log_message("rem_scene_listeners failed")
            
            
            try:
                self.rem_xFader_listeners()
            except:
                self.log_message("rem_xFader_listeners failed")
            
            
            try:
                self.rem_tempo_listener()
            except:
                self.log_message("rem_tempo_listener failed")
            
            
            try:
                self.rem_overdub_listener()
            except:
                self.log_message("rem_overdub_listener failed")
            
            
            try:
                self.rem_metronome_listener()
            except:
                self.log_message("rem_metronome_listener failed")
            
            
           
            try:
                self.rem_session_record_listener()
                self.rem_session_record_status_listener()
                self.rem_re_enable_automation_enabled_listener()
                self.rem_session_automation_record_listener()
                self.rem_arrangement_overdub_listener()

            except:
                self.log_message("remove live 9 listeners failed")


            try:
                self.rem_record_listener()
            except:
                self.log_message("rem_record_listener failed")

            try:
                self.rem_scenes_listener()
            except:
                self.log_message("rem_scenes_listener failed")
            
            try:
                self.rem_tracks_listener()
            except:
                self.log_message("rem_tracks_listener failed")
            
            try:
                self.rem_all_device_listeners()
            except:
                self.log_message("rem_all_device_listeners failed")
            
            try:
                self.rem_transport_listener()
            except:
                self.log_message("rem_transport_listener failed")
            
            try:
                self.rem_scenes_listeners()
            except:
                self.log_message("rem_scenes_listeners failed")
            
            try:
                self.rem_quant_listeners()
            except:
                self.log_message("rem_quant_listeners failed")
                    
            self.oscServer.sendOSC('/remix/oscserver/shutdown', 1)
            self.oscServer.shutdown()

        except:
            self.oscServer.sendOSC('/remix/oscserver/shutdown', 1)
            self.oscServer.shutdown()
                
                


    def build_midi_map(self, midi_map_handle):
        #self.refresh_state()
        #self.add_device_listeners()
        """for i in range(0,127):
            for j in range (0,15):
                Live.MidiMap.forward_midi_cc(self.handle(), midi_map_handle, j, i)
            pass
        pass"""
    
    def refresh_state(self):
        pass

    def update_all_listeners(self):
        self.add_clip_listeners()
        self.add_mixer_listeners()
        self.add_scene_listeners()
        self.add_xFader_listeners()
        self.add_RxFader_listeners()
        self.add_tempo_listener()
        self.add_overdub_listener()
        self.add_metronome_listener()
        try:
            self.add_session_record_listener()
            self.add_session_record_status_listener()
            self.add_re_enable_automation_enabled_listener()
            self.add_session_automation_record_listener()
            self.add_arrangement_overdub_listener()
            self.oscServer.sendOSC('/remix/oscserver/startup', 2)
        
        except:
            self.oscServer.sendOSC("live/", 8)

        self.add_record_listener()
        self.add_tracks_listener()
        self.add_scenes_listener()
        self.add_device_listeners()
        self.add_transport_listener()
        self.add_scenes_listeners()
        self.add_quant_listeners()
        self.tracks_change()

    def update_track_listeners(self):
        self.add_clip_listeners()
        self.add_mixer_listeners()
        self.add_xFader_listeners()
        self.add_device_listeners()
    
    
    def update_return_listeners(self):
        self.add_mixer_listeners()
        self.add_RxFader_listeners()
        self.add_device_listeners()

    def update_scene_listeners(self):
        self.add_clip_listeners()
        self.add_scenes_listeners()
        self.add_scenes_listener()


    def update_state(self):
        i = 0
        for track in self.song().tracks:
            self.oscServer.sendOSC("/track/is_visible", (int(i), int(track.is_visible)))
            i = i+1
        self.oscServer.sendOSC("/track/update_state", (1))




######################################################################
# Add / Remove Listeners   
    def add_scene_listeners(self):
        self.rem_scene_listeners()
        if self.song().view.selected_scene_has_listener(self.scene_change) != 1:
            self.song().view.add_selected_scene_listener(self.scene_change)

        if self.song().view.selected_track_has_listener(self.track_change) != 1:
            self.song().view.add_selected_track_listener(self.track_change)
             
      
    def add_xFader_listeners(self):
        self.rem_xFader_listeners()
        tracks = self.song().tracks
        for tr in range (len(tracks)):
            track = tracks[tr]
            self.add_xfade_listener(track, tr)
    
    def add_xfade_listener(self, track, tr):
        cb = lambda :self.xfade_assign_changed(track, tr)
        if self.ablisten.has_key(track) != 1:
            track.mixer_device.add_crossfade_assign_listener(cb)
            self.ablisten[track] = cb
        else:
            pass
    
    def rem_xFader_listeners(self):
        for track in self.ablisten:
            if track != None:
                if track.mixer_device.crossfade_assign_has_listener(self.ablisten[track]) == 1:
                    track.mixer_device.remove_crossfade_assign_listener(self.ablisten[track])
            else:
                pass
        self.ablisten = {}


    def xfade_assign_changed(self, track, tr):
        assign = 0
        assign = track.mixer_device.crossfade_assign
        self.oscServer.sendOSC("/track/crossfade_assign", (int(tr), int(assign)))
                
    
    
    
    
    def add_RxFader_listeners(self):
        self.rem_RxFader_listeners()
        tracks = self.song().return_tracks
        for tr in range (len(tracks)):
            track = tracks[tr]
            self.add_Rxfade_listener(track, tr)
    
    def add_Rxfade_listener(self, track, tr):
        cb = lambda :self.Rxfade_assign_changed(track, tr)
        if self.Rablisten.has_key(track) != 1:
            track.mixer_device.add_crossfade_assign_listener(cb)
            self.Rablisten[track] = cb
        else:
            pass
    
    def rem_RxFader_listeners(self):
        for track in self.Rablisten:
            if track != None:
                if track.mixer_device.crossfade_assign_has_listener(self.Rablisten[track]) == 1:
                    track.mixer_device.remove_crossfade_assign_listener(self.Rablisten[track])
            else:
                pass
        self.Rablisten = {}
    
    
    def Rxfade_assign_changed(self, track, tr):
        assign = 0
        assign = track.mixer_device.crossfade_assign
        self.oscServer.sendOSC("/return/crossfade_assign", (int(tr), int(assign)))                    

    
    
    
    
    
    def rem_scene_listeners(self):
        if self.song().view.selected_scene_has_listener(self.scene_change) == 1:
            self.song().view.remove_selected_scene_listener(self.scene_change)
            
        if self.song().view.selected_track_has_listener(self.track_change) == 1:
            self.song().view.remove_selected_track_listener(self.track_change)

      

    def track_change(self):
        selected_track = self.song().view.selected_track
        tracks = self.song().tracks
        returns = self.song().return_tracks

        index = 0
        selected_index = 0
        for track in tracks:
            if track == selected_track:
                selected_index = index
                self.oscServer.sendOSC("/set/selected_track", (0, (selected_index)))
            index = index + 1


        
        index = 0
        for ret in returns:
            if ret == selected_track:
                    selected_index = index
                    self.oscServer.sendOSC("/set/selected_track", (2, (selected_index)))
            index = index + 1


        if selected_track == self.song().master_track:
            self.oscServer.sendOSC("/set/selected_track", 1)

            

    def scene_change(self):
        selected_scene = self.song().view.selected_scene
        scenes = self.song().scenes
        index = 0
        selected_index = 0
        for scene in scenes:
            index = index + 1        
            if scene == selected_scene:
                selected_index = index
                
        if selected_index != self.scene:
            self.scene = selected_index
            self.oscServer.sendOSC("/set/selected_scene", (selected_index))
	
    def add_tempo_listener(self):
        self.rem_tempo_listener()
            
        if self.song().tempo_has_listener(self.tempo_change) != 1:
            self.song().add_tempo_listener(self.tempo_change)
        
    def rem_tempo_listener(self):
        if self.song().tempo_has_listener(self.tempo_change) == 1:
            self.song().remove_tempo_listener(self.tempo_change)
    
    def tempo_change(self):
        tempo = LiveUtils.getTempo()
        self.oscServer.sendOSC("/set/tempo", (tempo))

    def add_quant_listeners(self):
        self.rem_quant_listeners()

        if self.song().clip_trigger_quantization_has_listener(self.quant_change) != 1:
            self.song().add_clip_trigger_quantization_listener(self.quant_change)
            
        if self.song().midi_recording_quantization_has_listener(self.quant_change) != 1:
            self.song().add_midi_recording_quantization_listener(self.quant_change)
        
    def rem_quant_listeners(self):
        if self.song().clip_trigger_quantization_has_listener(self.quant_change) == 1:
            self.song().remove_clip_trigger_quantization_listener(self.quant_change)
        if self.song().midi_recording_quantization_has_listener(self.quant_change) == 1:
            self.song().remove_midi_recording_quantization_listener(self.quant_change)

    def quant_change(self):
        tquant = self.song().clip_trigger_quantization
        rquant = self.song().midi_recording_quantization
        self.oscServer.sendOSC("/set/quantization", (int(self.song().clip_trigger_quantization), int(self.song().midi_recording_quantization)))   
        
	
    def add_transport_listener(self):
        if self.song().is_playing_has_listener(self.transport_change) != 1:
            self.song().add_is_playing_listener(self.transport_change)
        #if self.song().current_song_time_has_listener(self.songtime_change) != 1:
            #self.song().add_current_song_time_listener(self.songtime_change)
            
    def rem_transport_listener(self):
        if self.song().is_playing_has_listener(self.transport_change) == 1:
            self.song().remove_is_playing_listener(self.transport_change)
        #if self.song().master_track.mixer_device.cue_volume(self.cuelevel) == 1:
            #self.song().master_track.mixer_device.addc(self.cuev level)
    
    def transport_change(self):
        self.oscServer.sendOSC("/set/playing_status", (self.song().is_playing and 2 or 1))

    def songtime_change(self):
        denom = self.song().signature_denominator
        numer = self.song().signature_numerator
        self.oscServer.sendOSC("/set/playing_position", (self.song().current_song_time,float(numer),float(denom)))


    def add_session_record_listener(self):
        self.rem_session_record_listener()
        
        if self.song().session_record_has_listener(self.session_record_change) != 1:
            self.song().add_session_record_listener(self.session_record_change)

    def rem_session_record_listener(self):
        if self.song().session_record_has_listener(self.session_record_change) == 1:
            self.song().remove_session_record_listener(self.session_record_change)


    def add_session_record_status_listener(self):
        self.rem_session_record_status_listener()
        
        if self.song().session_record_status_has_listener(self.session_record_status_changed) != 1:
            self.song().add_session_record_status_listener(self.session_record_status_changed)
    
    def rem_session_record_status_listener(self):
        if self.song().session_record_status_has_listener(self.session_record_status_changed) == 1:
            self.song().remove_session_record_status_listener(self.session_record_status_changed)


    def add_re_enable_automation_enabled_listener(self):
        self.rem_re_enable_automation_enabled_listener()
        
        if self.song().re_enable_automation_enabled_has_listener(self.re_enable_automation_enabled_changed) != 1:
            self.song().add_re_enable_automation_enabled_listener(self.re_enable_automation_enabled_changed)
    
    def rem_re_enable_automation_enabled_listener(self):
        if self.song().re_enable_automation_enabled_has_listener(self.re_enable_automation_enabled_changed) == 1:
            self.song().remove_re_enable_automation_enabled_listener(self.re_enable_automation_enabled_changed)



    def add_session_automation_record_listener(self):
        self.rem_session_automation_record_listener()
        
        if self.song().session_automation_record_has_listener(self.session_automation_record_change) != 1:
            self.song().add_session_automation_record_listener(self.session_automation_record_change)
    
    def rem_session_automation_record_listener(self):
        if self.song().session_automation_record_has_listener(self.session_automation_record_change) == 1:
            self.song().remove_session_automation_record_listener(self.session_automation_record_change)

    
    def add_arrangement_overdub_listener(self):
        self.rem_arrangement_overdub_listener()
        
        if self.song().arrangement_overdub_has_listener(self.overdub_change) != 1:
            self.song().add_arrangement_overdub_listener(self.overdub_change)
    
    def rem_arrangement_overdub_listener(self):
        if self.song().arrangement_overdub_has_listener(self.overdub_change) == 1:
            self.song().remove_arrangement_overdub_listener(self.overdub_change)



    def session_record_change(self):
        overdub = self.song().session_record
        self.oscServer.sendOSC("/live/set/session_record", (int(overdub)+1))
    
        trackNumber = 0
        numberOfTracks = len(self.song().tracks)
        for i in range(numberOfTracks):
            track = self.song().tracks[i]
            if track.can_be_armed == 1:
                if track.arm == 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            tid = trackNumber
                            cid = track.playing_slot_index
                            if track.clip_slots[cid].clip.is_audio_clip == 0:
                                if overdub == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
                                else:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                            else:
                                self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
        
            trackNumber = trackNumber+1
    

    def session_record_status_changed(self):
        overdub = self.song().session_record_status
        self.oscServer.sendOSC("/live/set/session_record_status", (int(overdub)+1))

    def re_enable_automation_enabled_changed(self):
        overdub = self.song().re_enable_automation_enabled
        self.oscServer.sendOSC("/live/set/re_enable_automation_enabled", (int(overdub)+1))

    def session_automation_record_change(self):
        overdub = self.song().session_automation_record
        self.oscServer.sendOSC("/live/set/session_automation_record", (int(overdub)+1))

    
    
    def session_record_chang(self, msg):
        
        session_record = msg[2]
        
        self.song().session_record = session_record
    
    def sesion_capture_midi(self, msg):
            
        self.song().capture_midi()
    
    
    def session_record_status_chang(self, msg):
        
        newActive = 0

        selected_scene = self.song().view.selected_scene

        index = 0
        selected_index = 0
        for scene in self.song().scenes:
            if scene == selected_scene:
                selected_index = index
            index = index + 1

        

        tracks = self.song().tracks
        
        for track in tracks:
            if track.can_be_armed:
                if track.arm:
                    if track.clip_slots[selected_index].clip != None:
                        newActive = 1;
                        break

        if newActive == 1:
            
            maxScenes = len(self.song().scenes)
            startIndex = selected_index
            sceneIsEmpty = 0
            newSceneIndex = 0
            
            for i in range(startIndex, maxScenes):
                sceneIsEmpty = 1
                for track in tracks:
                    if track.can_be_armed:
                        if track.arm:
                            if track.clip_slots[i].clip != None:
                                sceneIsEmpty = 0;

                                break
                if sceneIsEmpty == 1:
                    newSceneIndex = i
                    break
            
            if len(self.song().scenes) == newSceneIndex:
                self.song().create_scene()
            
            newScene = self.song().scenes[newSceneIndex]
            self.song().view.selected_scene = newScene

            for track in tracks:
                if track.can_be_armed:
                    if track.arm:
                        track.stop_all_clips()
                            




    def re_enable_automation_enabled_chang(self, msg):
        self.song().re_enable_automation()
    
    
    def session_automation_record_chang(self, msg):
        
        session_automation_record = msg[2]
        
        self.song().session_automation_record = session_automation_record


    def add_overdub_listener(self):
        self.rem_overdub_listener()
    
        if self.song().overdub_has_listener(self.overdub_change) != 1:
            self.song().add_overdub_listener(self.overdub_change)
	    
    def rem_overdub_listener(self):
        if self.song().overdub_has_listener(self.overdub_change) == 1:
            self.song().remove_overdub_listener(self.overdub_change)

    def add_metronome_listener(self):
        self.rem_metronome_listener()
    
        if self.song().metronome_has_listener(self.metronome_change) != 1:
            self.song().add_metronome_listener(self.metronome_change)
	    
    def rem_metronome_listener(self):
        if self.song().metronome_has_listener(self.metronome_change) == 1:
            self.song().remove_metronome_listener(self.metronome_change)

    def metronome_change(self):
        metronome = LiveUtils.getSong().metronome
        self.oscServer.sendOSC("/set/metronome_status", (int(metronome) + 1))
        
    def overdub_change(self):
        try:
            overdub = LiveUtils.getSong().arrangement_overdub
        except:
            overdub = LiveUtils.getSong().overdub

        self.oscServer.sendOSC("/set/overdub_status", (int(overdub) + 1))
        trackNumber = 0
        if self.application().get_major_version() == 8:
            for track in self.song().tracks:
                if track.can_be_armed == 1:
                    if track.arm == 1:
                        if track.playing_slot_index != -2:
                            tid = trackNumber
                            cid = track.playing_slot_index
                            if track.clip_slots[cid].clip.is_audio_clip == 0:
                                if overdub == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
                                else:
                                    self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                            else:
                                self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))
        
                trackNumber = trackNumber+1



    def add_record_listener(self):
        self.rem_record_listener()
    
        if self.song().record_mode_has_listener(self.record_change) != 1:
            self.song().add_record_mode_listener(self.record_change)
	    
    def rem_record_listener(self):
        if self.song().record_mode_has_listener(self.record_change) == 1:
            self.song().remove_record_mode_listener(self.record_change)

    def record_change(self):
        record = LiveUtils.getSong().record_mode
        self.oscServer.sendOSC("/set/recording_status", (int(record) + 1))
	
    def add_tracks_listener(self):
        self.rem_tracks_listener()
    
        if self.song().tracks_has_listener(self.tracks_change) != 1:
            self.song().add_tracks_listener(self.tracks_change)
    
        if self.song().visible_tracks_has_listener(self.update_state) != 1:
            self.song().add_visible_tracks_listener(self.update_state)
        
        if self.song().return_tracks_has_listener(self.returns_change) != 1:
            self.song().add_return_tracks_listener(self.returns_change)

    def rem_tracks_listener(self):
        if self.song().tracks_has_listener(self.tracks_change) == 1:
            self.song().remove_tracks_listener(self.tracks_change)
        
        if self.song().visible_tracks_has_listener(self.update_state) == 1:
            self.song().remove_visible_tracks_listener(self.update_state)
        
        if self.song().return_tracks_has_listener(self.returns_change) == 1:
            self.song().remove_return_tracks_listener(self.returns_change)
    
    def tracks_change(self):
        self.update_track_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))

    def returns_change(self):
        self.update_return_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))

    def add_scenes_listener(self):
        self.rem_scenes_listener()
    
        if self.song().scenes_has_listener(self.scenes_change) != 1:
            self.song().add_scenes_listener(self.scenes_change)


    def scenes_change(self):
        self.update_scene_listeners()
        self.oscServer.sendOSC("/server/refresh", (1))

    
    def rem_scenes_listener(self):
        if self.song().scenes_has_listener(self.scenes_change) == 1:
            self.song().remove_scenes_listener(self.scenes_change)

            
    def rem_clip_listeners(self):
        self.log("** Remove Listeners **")
    
        for slot in self.slisten:
            if slot != None:
                if slot.has_clip_has_listener(self.slisten[slot]) == 1:
                    slot.remove_has_clip_listener(self.slisten[slot])
                    
        self.slisten = {}
    

        for slot in self.sslisten:
            if slot != None:
                if slot.has_stop_button_has_listener(self.sslisten[slot]) == 1:
                    slot.remove_has_stop_button_listener(self.sslisten[slot])
                    
        self.sslisten = {}
    
        
        for clip in self.clisten:
            if clip != None:
                if clip.playing_status_has_listener(self.clisten[clip]) == 1:
                    clip.remove_playing_status_listener(self.clisten[clip])
                
        self.clisten = {}

        for clip in self.pplisten:
            if clip != None:
                if clip.playing_position_has_listener(self.pplisten[clip]) == 1:
                    clip.remove_playing_position_listener(self.pplisten[clip])
                
        self.pplisten = {}
    

        for clip in self.cnlisten:
            if clip != None:
                if clip.name_has_listener(self.cnlisten[clip]) == 1:
                    clip.remove_name_listener(self.cnlisten[clip])
                
        self.cnlisten = {}

        for clip in self.cclisten:
            if clip != None:
                if clip.color_has_listener(self.cclisten[clip]) == 1:
                    clip.remove_color_listener(self.cclisten[clip])
                
        self.cclisten = {}

        for key in self.noteListeners:
            if clip != None:
                if clip.notes_has_listener(self.noteListeners[key]) == 1:
                    clip.remove_notes_listener(self.noteListeners[key])

        self.noteListeners = {}

    
    def add_scenes_listeners(self):
        self.rem_scenes_listeners()
        scenes = self.song().scenes
        for sc in range (len(scenes)):
            scene = scenes[sc]
            self.add_scenelistener(scene, sc)

    def rem_scenes_listeners(self):
        for scene in self.sclisten:
            if scene != None:
                if scene.color_has_listener(self.sclisten[scene]) == 1:
                    scene.remove_color_listener(self.sclisten[scene])
            else:
                pass
        self.sclisten = {}

        for scene in self.snlisten:
            if scene != None:
                if scene.name_has_listener(self.snlisten[scene]) == 1:
                    scene.remove_name_listener(self.snlisten[scene])
            else:
                pass
        self.snlisten = {}
        
        for scene in self.stlisten:
            if scene != None:
                if scene.is_triggered_has_listener(self.stlisten[scene]) == 1:
                    scene.remove_is_triggered_listener(self.stlisten[scene])
            else:
                pass
        self.stlisten = {}
            

    def add_scenelistener(self, scene, sc):
        cb = lambda :self.scene_color_changestate(scene, sc)
        if self.sclisten.has_key(scene) != 1:
            scene.add_color_listener(cb)
            self.sclisten[scene] = cb
        else:
            pass
            
        cb2 = lambda :self.scene_name_changestate(scene, sc)
        if self.snlisten.has_key(scene) != 1:
            scene.add_name_listener(cb2)
            self.snlisten[scene] = cb2
        else:
            pass
                
        cb3 = lambda :self.scene_triggered(scene, sc)
        if self.stlisten.has_key(scene) != 1:
            scene.add_is_triggered_listener(cb3)
            self.stlisten[scene] = cb3
        else:
            pass
        

    def scene_color_changestate(self, scene, sc):
        nm = ""
        nm = scene.name
        if scene.color == 0:
            self.oscServer.sendOSC("/scene", (sc, repr3(nm), 0))
        else:
            self.oscServer.sendOSC("/scene", (sc, repr3(nm), scene.color))

    def scene_name_changestate(self, scene, sc):
        nm = ""
        nm = scene.name
        if scene.color == 0:
            self.oscServer.sendOSC("/scene", (sc, repr3(nm), 0))
        else:
            self.oscServer.sendOSC("/scene", (sc, repr3(nm), scene.color))

    def scene_triggered(self, scene, sc):
        
        self.oscServer.sendOSC("/scene/fired", int(sc+1))



    def add_clip_listeners(self):
        self.rem_clip_listeners()
        tracks = self.getslots()
        for track in range(len(tracks)):
            for clip in range(len(tracks[track])):
                c = tracks[track][clip]
                if c.clip != None:
                    self.add_cliplistener(c.clip, track, clip) 
                self.add_slotlistener(c, track, clip)
                
    def add_cliplistener(self, clip, tid, cid):
        cb = lambda :self.clip_changestate(clip, tid, cid)
        
        if self.clisten.has_key(clip) != 1:
            clip.add_playing_status_listener(cb)
            self.clisten[clip] = cb
        
        #if clip.is_audio_clip == 0:
        #cb4 = lambda :self.notesChanged(tid, cid, clip)
        #if self.noteListeners.has_key(clip) != 1:
        # clip.add_notes_listener(cb4)
        # self.noteListeners[clip] = cb4
            

        cb3 = lambda :self.clip_name(clip, tid, cid)
        if self.cnlisten.has_key(clip) != 1:
            clip.add_name_listener(cb3)
            self.cnlisten[clip] = cb3

        if self.cclisten.has_key(clip) != 1:
            clip.add_color_listener(cb3)
            self.cclisten[clip] = cb3
                

    def add_slotlistener(self, slot, tid, cid):
        cb = lambda :self.slot_changestate(slot, tid, cid)

        if self.slisten.has_key(slot) != 1:
            slot.add_has_clip_listener(cb)
            self.slisten[slot] = cb

        cb2 = lambda :self.stop_changestate(slot, tid, cid)
        if self.sslisten.has_key(slot) != 1:
            tracks = self.song().tracks
            track = tracks[tid]
            if track.is_foldable != 1:
                slot.add_has_stop_button_listener(cb2)
                self.sslisten[slot] = cb2
            else:
                pass


    
    def rem_mixer_listeners(self):
        # Master Track
        for type in ("volume", "panning", "crossfader"):
            for tr in self.masterlisten[type]:
                if tr != None:
                    cb = self.masterlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")

        # Normal Tracks
        for type in ("arm", "solo", "mute", "current_monitoring_state"):
            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                    
                    if type == "arm":
                        if tr.can_be_armed == 1:
                            if tr.arm_has_listener(cb) == 1:
                                tr.remove_arm_listener(cb)
                    elif type == "current_monitoring_state":
                            if tr.can_be_armed == 1:
                                if tr.current_monitoring_state_has_listener(cb) == 1:
                                    tr.remove_current_monitoring_state_listener(cb)    
                    else:
                        test = eval("tr." + type+ "_has_listener(cb)")
                
                        if test == 1:
                            eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.mlisten["sends"]:
            if tr != None:
                for send in self.mlisten["sends"][tr]:
                    if send != None:
                        cb = self.mlisten["sends"][tr][send]

                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)
                        
                        
        for tr in self.mlisten["name"]:
            if tr != None:
                cb = self.mlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)

        for tr in self.mlisten["color"]:
            if tr != None:
                cb = self.mlisten["color"][tr]

                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
                    

        for tr in self.mlisten["oml"]:
            if tr != None:
                cb = self.mlisten["oml"][tr]

                if tr.output_meter_left_has_listener(cb) == 1:
                    tr.remove_output_meter_left_listener(cb)                    

        for tr in self.mlisten["omr"]:
            if tr != None:
                cb = self.mlisten["omr"][tr]

                if tr.output_meter_right_has_listener(cb) == 1:
                    tr.remove_output_meter_right_listener(cb)
                    
        # Return Tracks                
        for type in ("solo", "mute"):
            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr." + type+ "_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.rlisten["sends"]:
            if tr != None:
                for send in self.rlisten["sends"][tr]:
                    if send != None:
                        cb = self.rlisten["sends"][tr][send]
                
                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)

        for tr in self.rlisten["name"]:
            if tr != None:
                cb = self.rlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)

        for tr in self.rlisten["color"]:
            if tr != None:
                cb = self.rlisten["color"][tr]
                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
                    
        self.mlisten = { "solo": {}, "mute": {}, "arm": {}, "current_monitoring_state": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "color": {} }
        self.rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {}  }
        self.masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }
    
    
    def add_mixer_listeners(self):
        self.rem_mixer_listeners()
        
        # Master Track
        tr = self.song().master_track
        for type in ("volume", "panning", "crossfader"):
            self.add_master_listener(0, type, tr)
        
        #self.add_meter_listener(0, tr, 2)
        
        # Normal Tracks
        tracks = self.song().tracks
        for track in range(len(tracks)):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 0)
            
            #if tr.has_audio_output:
                #self.add_meter_listener(track, tr)                
            
            for type in ("arm", "solo", "mute", "current_monitoring_state"):
                if type == "arm":
                    if tr.can_be_armed == 1:
                        self.add_mixert_listener(track, type, tr)

                elif type == "current_monitoring_state":
                    if tr.can_be_armed == 1:          
                        self.add_mixert_listener(track, type, tr)
                        
                else:
                    self.add_mixert_listener(track, type, tr)
                
            for type in ("volume", "panning"):
                self.add_mixerv_listener(track, type, tr)
                
            for sid in range(len(tr.mixer_device.sends)):
                self.add_send_listener(track, tr, sid, tr.mixer_device.sends[sid])
        
        # Return Tracks
        tracks = self.song().return_tracks
        for track in range(len(tracks)):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 1)
            #self.add_meter_listener(track, tr, 1)
            
            for type in ("solo", "mute"):
                self.add_retmixert_listener(track, type, tr)
                
            for type in ("volume", "panning"):
                self.add_retmixerv_listener(track, type, tr)
            
            for sid in range(len(tr.mixer_device.sends)):
                self.add_retsend_listener(track, tr, sid, tr.mixer_device.sends[sid])
    
    
    # Add track listeners
    def add_send_listener(self, tid, track, sid, send):
        if self.mlisten["sends"].has_key(track) != 1:
            self.mlisten["sends"][track] = {}
                    
        if self.mlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send)
            
            self.mlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_mixert_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")
            
    def add_mixerv_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")

    # Add master listeners
    def add_master_listener(self, tid, type, track):
        if self.masterlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 2)
            
            self.masterlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")
            
            
    # Add return listeners
    def add_retsend_listener(self, tid, track, sid, send):
        if self.rlisten["sends"].has_key(track) != 1:
            self.rlisten["sends"][track] = {}
                    
        if self.rlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send, 1)
            
            self.rlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_retmixert_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")
            
    def add_retmixerv_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")      


    # Track name listener
    def add_trname_listener(self, tid, track, ret = 0):
        cb = lambda :self.trname_changestate(tid, track, ret)

        if ret == 1:
            if self.rlisten["name"].has_key(track) != 1:
                self.rlisten["name"][track] = cb
            if self.rlisten["color"].has_key(track) != 1:
                self.rlisten["color"][track] = cb

        else:
            if self.mlisten["name"].has_key(track) != 1:
                self.mlisten["name"][track] = cb
            if self.mlisten["color"].has_key(track) != 1:
                self.mlisten["color"][track] = cb

        
        track.add_name_listener(cb)
        try:
            track.add_color_listener(cb)
        except:
            pass
        
    # Output Meter Listeners
    def add_meter_listener(self, tid, track, r = 0):
        cb = lambda :self.meter_changestate(tid, track, 0, r)

        if self.mlisten["oml"].has_key(track) != 1:
            self.mlisten["oml"][track] = cb

        track.add_output_meter_left_listener(cb)

 

######################################################################
# Listener Callbacks
        
    # Clip Callbacks
    def clip_name(self, clip, tid, cid):
        ascnm = ""
        nm = ""
        play = 0
        if clip.name != None:
            nm = cut_string(clip.name)
            #ascnm = (nm.encode('ascii', 'replace'))
        if clip.is_playing == 1:
            play = 1
        if clip.is_triggered == 1:
            play = 2
        if clip.is_recording == 1:
            if clip.is_playing == 1:
                play = 3

        nm = repr3(nm)
        self.oscServer.sendOSC('/clip', (tid, cid, nm, clip.color, play))


    def clip_loopchanged(self, clip, tid, cid):
        
        if self.isCheckingLoop != 1:
            self.isCheckingLoop = 1
            self.oscServer.sendOSC('/clip/loopchanged', (tid, cid))
        else:
            self.isCheckingLoop = 0


    def clip_position(self, clip, tid, cid):
        """if clip.is_playing:
            self.oscServer.sendOSC('/live/clip/position', (tid, cid, clip.playing_position, clip.length, clip.loop_start, clip.loop_end))"""
        
    def stop_changestate(self, slot, tid, cid):
        if slot.clip != None:
            pass
        else:
            if slot.has_stop_button == 1:
                self.oscServer.sendOSC('/clip', (tid, cid, "stop", 2500134, 0))
                self.oscServer.sendOSC('/clipslot/stop', (tid, cid))
            else:
                self.oscServer.sendOSC('/clipslot/empty', (tid, cid))

                


    
    def slot_changestate(self, slot, tid, cid):
        ascnm = ""
        nm = ""
        # Added new clip
        if slot.clip != None:
            self.add_cliplistener(slot.clip, tid, cid)
            play = 0
            if slot.clip.name != None:
                nm = cut_string(slot.clip.name)
                #ascnm = (nm.encode('ascii', 'replace'))
            if slot.clip.is_playing == 1:
                play = 1
 
            if slot.clip.is_triggered == 1:
                play = 2

            if slot.clip.is_recording == 1:
                if slot.clip.is_playing == 1:
                    play = 3
                    if self.onetap == 1:
                        slot.clip.fire()
                    else:
                        pass
            
                else:
                    pass
            else:
                pass
            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, play))
            self.oscServer.sendOSC('/clip', (tid, cid, repr3(nm), slot.clip.color, play))
        
            clip = slot.clip

            is_audio_clip = int(clip.is_audio_clip)
            
            isLooping = int(clip.looping)
            is_audio_clip = int(clip.is_audio_clip)
            
            warp = 0
            if is_audio_clip == 1:
                warp = int(clip.warping)
            else:
                pass
            loop_start = clip.loop_start
            loop_end = clip.loop_end
    
            try:
                start = clip.start_marker
                end = clip.end_marker
            except:
                start = clip.loop_start
                end = clip.loop_end


            self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
    
        else:
            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 0))
            self.stop_changestate(slot, tid, cid)
            if slot.has_stop_button_has_listener != 1:
                cb2 = lambda :self.stop_changestate(slot, tid, cid)
                slot.add_has_stop_button_listener(cb2)
            if self.clisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_status_listener(self.clisten[slot.clip])
                
            if self.pplisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_position_listener(self.pplisten[slot.clip])

            if self.cnlisten.has_key(slot.clip) == 1:
                slot.clip.remove_name_listener(self.cnlisten[slot.clip])

            if self.cclisten.has_key(slot.clip) == 1:
                slot.clip.remove_color_listener(self.cclisten[slot.clip])
            
            if self.noteListeners.has_key(slot.clip) == 1:
                slot.clip.remove_notes_listener(self.noteListeners[slot.clip])
        
                
    
    
    def clip_changestate(self, clip, x, y):
        playing = 0
        
        if clip.is_playing == 1:
            playing = 1
            if clip.is_recording == 1:
                playing = 3
            if self.song().tracks[x].arm == 1 and clip.is_audio_clip == 0:
                if self.song().overdub == 1:
                    playing = 3
                else:
                    playing = 1
        else:
            pass
        if clip.is_triggered == 1:
            playing = 2
        else:
            pass
        
        self.oscServer.sendOSC('/clip/playing_status', (x, y, playing))
        #self.log("Clip changed x:" + str(x) + " y:" + str(y) + " status:" + str(playing)) 
        
        
    # Mixer Callbacks
    def mixerv_changestate(self, type, tid, track, r = 0):
        val = eval("track.mixer_device." + type + ".value")
        types = { "panning": "pan", "volume": "volume", "crossfader": "crossfader" }
        
        if r == 2:
            self.oscServer.sendOSC('/master/' + types[type], (float(val)))
            if val == 0:
                self.oscServer.sendOSC('/master/' + types[type], (float(0.00000001)))

        elif r == 1:
            self.oscServer.sendOSC('/return/' + types[type], (tid, float(val)))
        else:
            self.oscServer.sendOSC('/track/' + types[type], (tid, val))        
        
    def mixert_changestate(self, type, tid, track, r = 0):
        val = eval("track." + type)
        if r == 1:
            self.oscServer.sendOSC('/return/' + type, (tid, int(val)))
        else:
            self.oscServer.sendOSC('/track/' + type, (tid, int(val)))
            if type == "arm":
                if val == 0:
                    if LiveUtils.getTrack(tid).playing_slot_index != -2:
                        cid = LiveUtils.getTrack(tid).playing_slot_index
                        self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))
                    else:
                        pass
                    
                elif val == 1:
                    if LiveUtils.getTrack(tid).playing_slot_index != -2:
                        cid = LiveUtils.getTrack(tid).playing_slot_index
                        if LiveUtils.getSong().overdub == 1 or LiveUtils.getTrack(tid).has_midi_input == 0:
                            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 3))

                        else:
                            self.oscServer.sendOSC('/clip/playing_status', (tid, cid, 1))

                    else:
                        pass
            else:
                pass

                    
    
    def send_changestate(self, tid, track, sid, send, r = 0):
        val = send.value
        
        if r == 1:
            self.oscServer.sendOSC('/return/send', (tid, sid, float(val)))   
        else:
            self.oscServer.sendOSC('/track/send', (tid, sid, float(val)))   


    # Track name changestate
    def trname_changestate(self, tid, track, r = 0):
        
        if r == 1:
            nm = track.name
            col = 0
            grouptrack = 0
            try:
                col = track.color
            except:
                pass
            #ascnm = (nm.encode('ascii', 'replace'))
            self.oscServer.sendOSC('/return', (tid, repr3(nm), col))
        else:
            nm = track.name
            col = 0
            is_midi_track = track.has_midi_input
            
            try:
                col = track.color
            except:
                pass
            if track.is_foldable == 1:
                grouptrack = 1
            else:
                grouptrack = 0
            #ascnm = (nm.encode('ascii', 'replace'))
            self.oscServer.sendOSC('/track', (tid, repr3(nm), col, grouptrack, int(is_midi_track)))

            
    # Meter Changestate
    def meter_changestate(self, tid, track, lr, r = 0):

        vall = track.output_meter_left
        #valr = track.output_meter_right
        tracknr = (tid - self.offsetx)
        if r == 2:
            if lr == 0:
                #if vall > valr:              
                self.oscServer.sendOSC('/live/master/meter', (float(vall)))
                #else:
                    #self.oscServer.sendOSC('/live/master/meter', (float(valr)))
        elif r == 1:
            if lr == 0:
                #if vall > valr:            
                self.oscServer.sendOSC('/live/return/meter', (tid, float(vall)))
                #else:
                    #self.oscServer.sendOSC('/live/return/meter', (tid, float(valr)))        
        else:
            if lr == 0:
                if tracknr >= 0:
                    if tracknr <= 7:
                        
                        #if vall > valr:
                        self.oscServer.sendOSC('/live/track/meter', (tracknr, float(vall)))
                        #else:
                            #self.oscServer.sendOSC('/live/track/meter', (tracknr, float(valr)))


        self.mlcache[track] = vall

                          
    
    # Device Listeners
    
    
    def add_device_listeners_for_track(self, track, tid, type):

        self.remove_device_listeners_of_track(track, tid, type)
        
        self.add_devices_listener(track, tid, type)

        key = '%s.%s' % (type, tid)

        self.prlisten[key] = {}
        self.parameters_listeners[key] = {}
        self.chainslisten[key] = {}

        self.chaindevicelisten[key] = {}
        self.drum_pad_listen[key] = {}

        drum_pad_listen = self.drum_pad_listen[key]

        a = Live.Application.get_application().get_major_version()
        number_of_steps = 0
        i = 0
        indices = []

        if len(track.devices) >= 1:

            for did in range(len(track.devices)):
                
                device = track.devices[did]
                lis = list(indices)
                """ self.oscServer.sendOSC("/NSLOG_REPLACE", "add_device_listeners_for_track from add_listener_for_device") """
                self.add_listener_for_device(track, tid, did, type, device, 0, lis, -1)
            


    def add_listener_for_device(self, track, tid, did, type, device, number_of_steps, indices, i):
        a = Live.Application.get_application().get_major_version()
        key = '%s.%s' % (type, tid)

        if i != -1:
            indices.append(int(i))
            number_of_steps = number_of_steps+1
        else:
            indic = []
            indices = list(indic)
        

        prlisten = self.prlisten[key]
        parameters_listeners = self.parameters_listeners[key]
        chaindevicelisten = self.chaindevicelisten[key]
        
        tr = device.canonical_parent
        
        num = len(tr.devices)
        lis = list(indices)


        cb = lambda :self.update_listeners_for_device(device, track, tid, did, type, num, number_of_steps, lis, -1)
        
        if parameters_listeners.has_key(device) != 1:
            #if device.class_name == 'OriginalSimpler':
            #self.oscServer.sendOSC("/NSLOG_REPLACE", "add_parameter_listener")
            device.add_parameters_listener(cb)
            parameters_listeners[device] = cb



        if a >= 9:
            if type == 0:
                if device.can_have_drum_pads == 1:
                    key = '%s.%s' % (type, tid)
                    drum_pad_listen = self.drum_pad_listen[key]
                    for drum_id in range(len(device.drum_pads)):
                        drum_pad = device.drum_pads[drum_id]
                        #self.oscServer.sendOSC("/NSLOG_REPLACE", "ADDING DRUM PAD LISTENER")
                        
                        self.add_drum_pad_listener(drum_pad_listen, drum_pad, int(tid), int(did), number_of_steps, lis)
        
        
            if device.can_have_chains == 1:
                
                chainslisten = self.chainslisten[key]
                if chainslisten.has_key(device) != 1:
                    device.add_chains_listener(cb)
                    chainslisten[device] = cb


                for chain_id in range(len(device.chains)):
                    chain = device.chains[chain_id]

                    self.add_chain_devices_listener(track, tid, type, chain)
                    
                    listt = list(indices)
                    listt.append(int(chain_id))

                    for device_id in range(len(chain.devices)):
                        dev = chain.devices[device_id]

                        lis = list(listt)
                        #self.oscServer.sendOSC("/NSLOG_REPLACE", "update add listener for device from itself" + device.name)

                        self.add_listener_for_device(track, tid, did, type, dev, number_of_steps, lis, device_id)
    
    
    
    
    

        #self.oscServer.sendOSC('/adding_device_listeners_for_device2', (int(type), int(tid), int(did), int(number_of_steps), tuple(indis)))
        
        #self.oscServer.sendOSC('/adding_device_listeners_for_device2', (tuple(indices)))


        if len(device.parameters) >= 1:
            for pid in range(len(device.parameters)):
                param = device.parameters[pid]
                self.add_parameter_listener(prlisten, param, int(tid), int(did), int(pid), int(type), int(number_of_steps), tuple(indices))

        #self.oscServer.sendOSC('/adding_device_listeners_for_device3', (tuple(indices)))




    def add_parameter_listener(self, prlisten, param, tid, did, pid, type, number_of_steps, indices):
        cb = lambda :self.param_changestate(param, int(tid), int(did), int(pid), int(type), int(number_of_steps), indices)
        if prlisten.has_key(param) != 1:
            param.add_value_listener(cb)
            prlisten[param] = cb


    
    def remove_device_listeners_of_track(self, track, tid, type):

        self.remove_devices_listener(track, tid, type)
        key = '%s.%s' % (type, tid)

        if self.prlisten.has_key(key) == 1:
            #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)

            prlisten = self.prlisten[key]

            for pr in prlisten:
                if pr != None:
                    ocb = prlisten[pr]
                    if pr.value_has_listener(ocb) == 1:
                        pr.remove_value_listener(ocb)
            del self.prlisten[key]
                                                    
           

        if self.parameters_listeners.has_key(key) == 1:
           #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)
           
            parameters_listeners = self.parameters_listeners[key]
               
            for pr in parameters_listeners:
                if pr != None:
                    ocb = parameters_listeners[pr]
                    if pr.parameters_has_listener(ocb) == 1:
                        pr.remove_parameters_listener(ocb)
            del self.parameters_listeners[key]
        

        if self.chainslisten.has_key(key) == 1:
            #self.oscServer.sendOSC('/live/track/device_listeners_found', 1)
            
            chainslisten = self.chainslisten[key]
            
            for dev in chainslisten:
                if dev != None:
                    ocb = chainslisten[dev]
                    if dev.chains_has_listener(ocb) == 1:
                        dev.remove_chains_listener(ocb)
            del self.chainslisten[key]
    
    
    
        if self.drum_pad_listen.has_key(track) == 1:

            drum_pad_listen = self.drum_pad_listen[key]
        
            for drum_pad in drum_pad_listen:
                if drum_pad != None:
                    ocb = drum_pad_listen[drum_pad]
                    if drum_pad.name_has_listener(ocb) == 1:
                        drum_pad.remove_name_listener(ocb)
            del self.drum_pad_listen[key]
            
    
    
    def add_device_listeners(self):
        self.do_add_device_listeners(self.song().tracks,0)
        self.do_add_device_listeners(self.song().return_tracks,2)
        self.do_add_device_listeners([self.song().master_track],1)
        self.add_app_device_listener()

        #self.oscServer.sendOSC('/track/adding_all_listeners', 2)

    def add_app_device_listener(self):
        self.rem_app_device_listener()
            
        if self.song().appointed_device_has_listener(self.device_changestate) != 1:
            self.song().add_appointed_device_listener(self.device_changestate)


    def rem_app_device_listener(self):
        if self.song().appointed_device_has_listener(self.device_changestate) == 1:
            self.song().remove_appointed_device_listener(self.device_changestate)
    
    
    def do_add_device_listeners(self, tracks, type):
        for tid in range(len(tracks)):
            track = tracks[tid]
            self.add_device_listeners_for_track(track, tid, type)


    def do_remove_device_listeners(self, tracks, type):
        for tid in range(len(tracks)):
            track = tracks[tid]
            self.remove_device_listeners_of_track(track, tid, type)

    def rem_all_device_listeners(self):
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 1)

        
        self.do_remove_device_listeners(self.song().tracks,0)
        self.do_remove_device_listeners(self.song().return_tracks,2)
        self.do_remove_device_listeners([self.song().master_track],1)
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 2)

        for key in self.drum_pad_listen:
        
            #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 3)
            drum_pad_listen = self.drum_pad_listen[key]
            for drum_pad in drum_pad_listen:
                if drum_pad != None:
                    ocb = drum_pad_listen[drum_pad]
                    if drum_pad.name_has_listener(ocb) == 1:
                        drum_pad.remove_name_listener(ocb)
    
        #self.oscServer.sendOSC('/live/track/removing_all_dev_listeners', 4)
        self.drum_pad_listen = {}


    
        
    def add_paramlistener(self, param, tid, did, pid, type):
        cb = lambda :self.param_changestate(param, tid, did, pid, type)
        
        if self.prlisten.has_key(param) != 1:
            param.add_value_listener(cb)
            self.prlisten[param] = cb

        

    def add_drum_pad_listener(self, drum_pad_listen, drum_pad, i, j, number_of_steps, indices):
        cb = lambda :self.drum_pad_changed(drum_pad, i, j, number_of_steps, indices)
        if drum_pad_listen.has_key(drum_pad) != 1:
            drum_pad.add_name_listener(cb)
            drum_pad_listen[drum_pad] = cb
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "ADDED DRUM PAD LISTENER")


    def add_drumpads_listener(self, device, i, j, number_of_steps, indices):
        cb = lambda :self.drum_pads_changed(device.drum_pads, i, j, number_of_steps, indices)
        if self.drum_pads_listen.has_key(device) != 1:
            device.add_drum_pads_listener(cb)
            self.drum_pads_listen[device] = cb


    def drum_pads_changed(self, drum_pads, i, j, number_of_steps, indices):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", str("DRUM PADSSS CHANGED !!!!!!!11111"))

        drum_pads_tuple = [0, i, j, number_of_steps]
        for index in range(number_of_steps * 2):
            drum_pads_tuple.append(int(indices[index]))

        for drum_pad in drum_pads:
            drum_pads_tuple.append(int(drum_pad.note))
            drum_pads_tuple.append(repr3(drum_pad.name))
            drum_pads_tuple.append(int(drum_pad.mute))
            drum_pads_tuple.append(int(drum_pad.solo))
        self.oscServer.sendOSC("/track/device/drumpads", tuple(drum_pads_tuple))
    

    def drum_pad_changed(self, drum_pad, i, j, number_of_steps, indices):
        #self.oscServer.sendOSC("/NSLOG_REPLACE", str("DRUM PAD CHANGED !!!!!!!11111"))

        drum_pad_tuple = [0, i, j, number_of_steps]
        for index in range(number_of_steps * 2):
            drum_pad_tuple.append(int(indices[index]))
                
        drum_pad_tuple.append(int(drum_pad.note))
        drum_pad_tuple.append(repr3(drum_pad.name))
        drum_pad_tuple.append(int(drum_pad.mute))
        drum_pad_tuple.append(int(drum_pad.solo))
        self.oscServer.sendOSC("/track/device/drumpad", tuple(drum_pad_tuple))


    
    def param_changestate(self, param, tid, did, pid, type, number_of_steps, indices):
        if type == 1:
            indis = [type, 0, did, pid, param.value, repr3(param.__str__()), number_of_steps]
            for index in indices:
                indis.append(index)
            self.oscServer.sendOSC('/master/device/parameter', (tuple(indis)))
        elif type == 2:
            indis = [type, tid, did, pid, param.value, repr3(param.__str__()), number_of_steps]
            for index in indices:
                indis.append(index)
            self.oscServer.sendOSC('/return/device/parameter', (tuple(indis)))
        else:
            indis = [type, tid, did, pid, param.value, repr3(param.__str__()), number_of_steps]
            for index in indices:
                indis.append(index)
            self.oscServer.sendOSC('/track/device/parameter', (tuple(indis)))
        


    def add_devices_listener(self, track, tid, type):

        key = '%s.%s' % (type, tid)

        cb = lambda :self.devices_changed(track, tid, type)
        if self.devices_listen.has_key(key) != 1:
            track.add_devices_listener(cb)
            self.devices_listen[key] = cb



    def add_chain_devices_listener(self, track, tid, type, chain):
    
        key = '%s.%s' % (type, tid)
        chaindevicelisten = self.chaindevicelisten[key]
        
        cb = lambda :self.devices_changed(track, tid, type)
        if chaindevicelisten.has_key(chain) != 1:
            chain.add_devices_listener(cb)
            chaindevicelisten[chain] = cb


    def device_changestate(self):
        
        #self.oscServer.sendOSC("/NSLOG_REPLACE", "Appointed device checked")

        self.oscServer.sendOSC('/selected_device', (0))

        device = self.song().appointed_device
        if device == None:
            return
        else:
            pass
        
        track = device.canonical_parent
        did = 0
        type = 0
        number_of_steps = 0
        indices = []

        while track.canonical_parent != self.song():

            if number_of_steps % 2 != 0:
                indices.append(self.tuple_idx(track.chains, device))
            else:
                indices.append(self.tuple_idx(track.devices, device))
    

            number_of_steps = number_of_steps + 1
            
            device = track
            track = device.canonical_parent



        if track.canonical_parent == self.song():

            did = self.tuple_idx(track.devices, device)
            
            tid = self.tuple_idx(self.song().tracks, track)
            type = 0

            if tid < 0:

                tid = self.tuple_idx(self.song().return_tracks, track)
                
                if tid >= 0:
                    type = 2
                else:
                    type = 1
                    tid = 0
        indis = [type, tid, did, int(number_of_steps/2)]

        for i in range(len(indices)):
            indis.append(int(indices[len(indices)-1-i]))
       
        self.oscServer.sendOSC('/selected_device', tuple(indis))

    def tuple_idx(self, tuple, obj):
        for i in xrange(0,len(tuple)):
            if (tuple[i] == obj):
                return i
        return -1
    

    def remove_devices_listener(self, track, tid, type):
        key = '%s.%s' % (type, tid)
        
        if self.devices_listen.has_key(key) == 1:
            ocb = self.devices_listen[key]
            if track.devices_has_listener(ocb) == 1:
                track.remove_devices_listener(ocb)
            del self.devices_listen[key]

        if self.chaindevicelisten.has_key(key) == 1:
                                                    
            chaindevicelisten = self.chaindevicelisten[key]
                                                    
            for pr in chaindevicelisten:
                if pr != None:
                    ocb = chaindevicelisten[pr]
                    if pr.devices_has_listener(ocb) == 1:
                        pr.remove_devices_listener(ocb)
            del self.chaindevicelisten[key]


    def send_update_for_device(self, device, track, tid, did, type, num, number_of_steps, indices, i):
        
        

        if i != -1:
            
            indices.append(int(i))
            number_of_steps = number_of_steps+1

        elif i == -1 and number_of_steps == 0:
            indic = []
            indices = list(indic)



        nm = repr3(device.name)
        params = device.parameters
        onoff = params[0].value
        numParams = len(params)
        cnam = repr3(device.class_name)
        
        
        tr = tid
        dev = did
        
        
        po = [type]
        po.append(int(tr))
        po.append(int(dev))
        
        is_selected = 0
        
        if device == self.song().appointed_device:
            is_selected = 1
        else:
            pass


        po2 = [type]
        po2.append(int(tr))
        po2.append(int(dev))
        po2.append(repr3(track.name))
        po2.append(repr3(device.name))
        po2.append(int(is_selected))
        
        po.append(int(number_of_steps))
        po2.append(int(number_of_steps))
        #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("PO2 len:"), int(len(po2)), int(number_of_steps)))


        for index in range(number_of_steps * 2):
            po.append(int(indices[index]))
            po2.append(int(indices[index]))

        #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("PO2 len after adding indices:"), int(len(po2)), int(number_of_steps)))


        for j in range(len(params)):
            para = params[j]
            po.append(para.min)
            po.append(para.max)
            po.append(para.is_quantized+1)
            val = para.value
            po2.append(float(val))
            po2.append(repr3(para.name))
            po2.append(repr3(para.__str__()))



        try:
            can_have_chains = device.can_have_chains
        except:
            can_have_chains = 0
            
        try:
            can_have_drumpads = device.can_have_drum_pads and device.has_drum_pads and device.class_name == 'MultiSampler' or device.class_name == "DrumGroupDevice"
        except:
            can_have_drumpads = 0
        
        if type == 0:

            
            po3 = [0, tid, did, nm, onoff, num, numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            self.oscServer.sendOSC("/track/device", (tuple(po3)))
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/track/device/parameters", tuple(po2))
            
            #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPADS with number of steps 123"), str(device.class_name)))
            if can_have_drumpads:
                
                #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPADS"), int(21)))
                drum_pads_tuple = [type, tid, did, number_of_steps]
                for index in range(number_of_steps * 2):
                    drum_pads_tuple.append(int(indices[index]))
                
                
                for drum_pad in device.drum_pads:
                    drum_pads_tuple.append(int(drum_pad.note))
                    drum_pads_tuple.append(repr3(drum_pad.name))
                    drum_pads_tuple.append(int(drum_pad.mute))
                    drum_pads_tuple.append(int(drum_pad.solo))
                    #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPAD"), repr3(drum_pad.name)))

                self.oscServer.sendOSC("/track/device/drumpads", tuple(drum_pads_tuple))
                #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPADS"), int(3)))
        
        elif type == 2:
            po3 = [2, tid, did, nm, onoff, num, numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            self.oscServer.sendOSC("/return/device", (tuple(po3)))
            
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/return/device/parameters", tuple(po2))
        
        elif type == 1:
            po3 = [1, 0, did, nm, onoff, num, numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))

            self.oscServer.sendOSC("/master/device", (tuple(po3)))

            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/master/device/parameters", tuple(po2))
        

        
        if can_have_chains == 1:
            for chain_id in range(len(device.chains)):
                chain = device.chains[chain_id]

                indis = list(indices)
                indis.append(int(chain_id))

                po3 = [type, tid, did, repr3(chain.name), number_of_steps]
                for index in range(number_of_steps * 2 + 1):
                    po3.append(int(indis[index]))


                self.oscServer.sendOSC("/device_chain", (tuple(po3)))
                
                for device_id in range(len(chain.devices)):
                    dev = chain.devices[device_id]
                    
                    lis = list(indis)
                    
                    self.send_update_for_device(dev, track, tid, did, type, len(chain.devices), number_of_steps, lis, device_id)





    def devices_changed(self, track, tid, type):
        a = Live.Application.get_application().get_major_version()
        
        
        for a_tid in range(len(LiveUtils.getSong().tracks)):
            atrack = LiveUtils.getSong().tracks[a_tid]
            if atrack == track:
                tid = a_tid
        
        self.oscServer.sendOSC("/devices_empty", (int(type), int(tid)))
        

        did = 0
        
        number_of_steps = 0
        i = 0
        indices = []
        
        for device in track.devices:
            
            lis = list(indices)

            self.send_update_for_device(device, track, tid, did, type, len(track.devices), number_of_steps, lis, -1)

            did = did+1

        self.oscServer.sendOSC('/devices_loaded', (int(type), int(tid)))
        self.add_device_listeners_for_track(track, int(tid), int(type))


