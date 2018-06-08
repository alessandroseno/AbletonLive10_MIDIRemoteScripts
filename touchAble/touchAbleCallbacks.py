"""
# Copyright (C) 2007 Rob King (rob@re-mu.org)
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
# Rob King <rob@e-mu.org> or visit http://www.e-mu.org
# 
# Additional touchAble development:
# (c) 2014 Sigabort, Lee Huddleston, ZeroConfig; admin@sigabort.co, http://sigabort.co

This file contains all the current Live OSC callbacks. 

"""
import Live
import RemixNet
import OSC
import LiveUtils
import time
import unicodedata

def repr2(input_str):
    try:
        output_st = unicodedata.normalize('NFKD', input_str).encode('ascii','ignore')
        if output_st != None:
            return output_st
        else:
            return ''
    except:
        x = repr(input_str)
        return x[2:-1]


    #encoding = "utf-8" # or iso-8859-15, or cp1252, or whatever encoding you use
    #unicode_string = input_str.decode(encoding)
    
    #nkfd_form = unicodedata.normalize('NFKD', unicode_string)
    #string = u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    #print string
    #return string

def cut_string2(input_str):
    info = (input_str[0:331] + '..') if len(input_str) > 333 else input_str
    return (info)

class touchAbleCallbacks:


    
    # LMH
    def __init__(self, c_instance, oscServer, touchAble):
        if oscServer:
            self.oscServer = oscServer
            self.callbackManager = oscServer.callbackManager
            self.oscClient = oscServer.oscClient
            self.c_instance = c_instance
            self.touchAble = touchAble
        else:
            return
        self.mlcache = []
        self.mrcache = []
        self.mmcache = 0
        self.mlcache = [-1 for i in range(200)]
        self.mrcache = [-1 for i in range(12)]
        self.mmcache = -1

        self.callbackManager.add(self.update, "/get/update")
        self.callbackManager.add(self.playClipCB, "/live/play/clip")
        self.callbackManager.add(self.nudgeupCB, "/nudgeup")
        self.callbackManager.add(self.trackxfaderCB, "/abAssign")
        self.callbackManager.add(self.trackxfaderCB, "/return/abAssign")
        self.callbackManager.add(self.nudgedownCB, "/nudgedown")
        self.callbackManager.add(self.foldTrackCB, "/foldTrack")
        self.callbackManager.add(self.cuelevelCB, "/cuelevel")
        self.callbackManager.add(self.doneCB, "/done")
        self.callbackManager.add(self.tempoCB, "/live/tempo")
        self.callbackManager.add(self.timeCB, "/live/time")
        self.callbackManager.add(self.nextCueCB, "/live/next/cue")
        self.callbackManager.add(self.prevCueCB, "/live/prev/cue")
        self.callbackManager.add(self.playCB, "/live/play")
        self.callbackManager.add(self.playContinueCB, "/live/play/continue")
        self.callbackManager.add(self.playSelectionCB, "/live/play/selection")
        self.callbackManager.add(self.playSceneCB, "/live/play/scene")  
        self.callbackManager.add(self.stopCB, "/live/stop")
        self.callbackManager.add(self.stopClipCB, "/live/stop/clip")
        self.callbackManager.add(self.stopTrackCB, "/live/stop/track")
        self.callbackManager.add(self.stopAllCB, "/live/stopall")
        self.callbackManager.add(self.scenesCB, "/live/scenes")
        self.callbackManager.add(self.tracksCB, "/script/load")
        self.callbackManager.add(self.returnsCB, "/live/returns")
        self.callbackManager.add(self.nameSceneCB, "/live/name/scene")
        self.callbackManager.add(self.sceneCB, "/live/scene")
        self.callbackManager.add(self.nameTrackCB, "/live/name/track")
        self.callbackManager.add(self.nameTrackBlockCB, "/live/name/trackblock")
        self.callbackManager.add(self.nameSceneBlockCB, "/live/name/sceneblock")
        self.callbackManager.add(self.volumeBlockCB, "/live/volumeblock")
        self.callbackManager.add(self.sendaBlockCB, "/live/sendablock")          
        self.callbackManager.add(self.sendbBlockCB, "/live/sendbblock")          
        self.callbackManager.add(self.sendcBlockCB, "/live/sendcblock")          
        self.callbackManager.add(self.senddBlockCB, "/live/senddblock")
        self.callbackManager.add(self.monitorBlockCB, "/live/monitorblock")
        self.callbackManager.add(self.deviceBlockCB, "/live/deviceblock")
        self.callbackManager.add(self.parameterblockCB, "/live/parameterblock")
        self.callbackManager.add(self.masterparameterblockCB, "/live/master/parameterblock")
        self.callbackManager.add(self.returnparameterblockCB, "/live/return/parameterblock")
        self.callbackManager.add(self.panBlockCB, "/live/panblock")          
        self.callbackManager.add(self.monitorTrackCB, "/live/monitor")
        self.callbackManager.add(self.armblockCB, "/live/armblock")
        self.callbackManager.add(self.muteblockCB, "/live/muteblock")
        self.callbackManager.add(self.soloblockCB, "/live/soloblock")
        self.callbackManager.add(self.nameClipCB, "/live/name/clip")
        self.callbackManager.add(self.nameClipBlockCB, "/live/name/clipblock")
        self.callbackManager.add(self.nameColorBlockCB, "/live/name/colorblock")   
        self.callbackManager.add(self.armTrackCB, "/arm")
        self.callbackManager.add(self.muteTrackCB, "/live/mute")
        self.callbackManager.add(self.soloTrackCB, "/solo")
        self.callbackManager.add(self.volumeCB, "/live/volume")
        self.callbackManager.add(self.panCB, "/live/pan")
        self.callbackManager.add(self.sendCB, "/live/send")
        self.callbackManager.add(self.pitchCB, "/live/pitch")
        self.callbackManager.add(self.trackJump, "/live/track/jump")
        self.callbackManager.add(self.trackInfoCB, "/live/track/info")
        self.callbackManager.add(self.undoCB, "/live/undo")
        self.callbackManager.add(self.redoCB, "/live/redo")
        self.callbackManager.add(self.playClipSlotCB, "/live/play/clipslot")
        self.callbackManager.add(self.releaseClipSlotCB, "/live/release/clipslot")
        self.callbackManager.add(self.clipplayBlockCB, "/live/playing")        
        self.callbackManager.add(self.viewSceneCB, "/live/scene/view")
        self.callbackManager.add(self.deviceSelect, "/live/deviceselect")
        self.callbackManager.add(self.viewTrackCB, "/live/track/view")
        self.callbackManager.add(self.arms, "/arms")
        self.callbackManager.add(self.solos, "/solos")
        self.callbackManager.add(self.volumes, "/volumes")
        self.callbackManager.add(self.abAssigns, "/abAssigns")
        self.callbackManager.add(self.sendas, "/sendas")
        self.callbackManager.add(self.sendbs, "/sendbs")
        self.callbackManager.add(self.sendcs, "/sendcs")
        self.callbackManager.add(self.sendds, "/sendds")
        self.callbackManager.add(self.pans, "/pans")
        self.callbackManager.add(self.monitors, "/monitors")
        self.callbackManager.add(self.mutes, "/mutes")
        self.callbackManager.add(self.createClip, "/clip/create")
        self.callbackManager.add(self.deleteClip, "/clip/delete")
        self.callbackManager.add(self.duplicateClip, "/clip/duplicate")
        self.callbackManager.add(self.createScene, "/scene/create")
        self.callbackManager.add(self.deleteScene, "/scene/delete")
        self.callbackManager.add(self.deleteTrack, "/track/delete")
        self.callbackManager.add(self.duplicateTrack, "/track/duplicate")
        self.callbackManager.add(self.duplicateScene, "/scene/duplicate")
        self.callbackManager.add(self.deleteReturn, "/return/delete")
        self.callbackManager.add(self.createMidiTrack, "/track/create_midi")
        self.callbackManager.add(self.createAudioTrack, "/track/create_audio")
        self.callbackManager.add(self.createReturnTrack, "/track/create_return")
        self.callbackManager.add(self.toggleStopButton, "/clip/has_stop_button")
        self.callbackManager.add(self.deleteDevice, "/device/delete")
        self.callbackManager.add(self.deleteReturnDevice, "/return_device/delete")
        self.callbackManager.add(self.deleteMasterDevice, "/master_device/delete")

        self.callbackManager.add(self.focusDevice, "/live/track/device/view")
        self.callbackManager.add(self.focusDevice, "/live/return/device/view")
        self.callbackManager.add(self.focusDevice, "/live/master/device/view")
        self.callbackManager.add(self.focusChain, "/live/track/chain/view")

        
        self.callbackManager.add(self.viewClipCB, "/live/clip/view")
        
        self.callbackManager.add(self.detailViewCB, "/live/detail/view")
        
        self.callbackManager.add(self.overdubCB, "/live/overdub")
        self.callbackManager.add(self.stateCB, "/live/state")
        self.callbackManager.add(self.clipInfoCB, "/live/clip/info")
        
        self.callbackManager.add(self.change_device_parameter, "/change_device_parameter")


        self.callbackManager.add(self.muteTrackCB, "/live/return/mute")
        self.callbackManager.add(self.soloTrackCB, "/live/return/solo")
        self.callbackManager.add(self.volumeCB, "/live/return/volume")
        self.callbackManager.add(self.panCB, "/live/return/pan")
        self.callbackManager.add(self.sendCB, "/live/return/send")        

        self.callbackManager.add(self.volumeCB, "/live/master/volume")
        self.callbackManager.add(self.panCB, "/live/master/pan")
        
        self.callbackManager.add(self.mdevicelistCB, "/live/master/devicelist")
        self.callbackManager.add(self.trackdeviceblockCB, "/live/trackdeviceblock")
        self.callbackManager.add(self.returndeviceblockCB, "/live/returndeviceblock")
        self.callbackManager.add(self.masterdeviceblockCB, "/live/masterdeviceblock")


        self.callbackManager.add(self.deviceCB, "/live/device")
        self.callbackManager.add(self.returndeviceCB, "/live/return/device")
        self.callbackManager.add(self.mdeviceCB, "/live/master/device")
        
        self.callbackManager.add(self.loopStateCB, "/live/clip/loopstate")
        
        self.callbackManager.add(self.loopStateCB, "/live/clip/loopstate_id")
        
        self.callbackManager.add(self.warpingCB, "/live/clip/warping")
        
        self.callbackManager.add(self.sigCB, "/live/clip/signature")

        self.callbackManager.add(self.crossfaderCB, "/live/master/crossfader")
        self.callbackManager.add(self.trackxfaderCB, "/live/track/crossfader")
        self.callbackManager.add(self.trackxfaderCB, "/live/return/crossfader")
        self.callbackManager.add(self.quantizationCB, "/live/quantization")
        self.callbackManager.add(self.recquantizationCB, "/live/recquantization")
        self.callbackManager.add(self.recordCB, "/live/record")
        self.callbackManager.add(self.metronomeCB, "/live/metronome")
        self.callbackManager.add(self.songpsCB, "/live/songps")
        self.callbackManager.add(self.rdevCB, "/returndevices")
        self.callbackManager.add(self.mdevCB, "/masterdevices")
        self.callbackManager.add(self.devCB, "/devicess")
        self.callbackManager.add(self.clipstuff, "/clipstuff")
        self.callbackManager.add(self.selectionCB, "/live/selection")
        self.callbackManager.add(self.quantsCB, "/quants")
        self.callbackManager.add(self.loopclipCB, "/loopclip")
        self.callbackManager.add(self.muteclipCB, "/muteclip")
        self.callbackManager.add(self.pitchcoarseCB, "/pitch")
        self.callbackManager.add(self.detuneCB, "/detune")
        self.callbackManager.add(self.startposCB, "/loopstart")
        self.callbackManager.add(self.endposCB, "/loopend")
        self.callbackManager.add(self.clipstartposCB, "/clipstart")
        self.callbackManager.add(self.clipendposCB, "/clipend")
        self.callbackManager.add(self.activateLoopCB, "/activateLoop")
        self.callbackManager.add(self.deactivateLoopCB, "/deactivateLoop")
        self.callbackManager.add(self.loopInfo, "/clip/loop_info")
        self.callbackManager.add(self.loadChildren, "/browser/load_children")
        #self.callbackManager.add(self.broadcast, "/broadcast");
        self.callbackManager.add(self.changeGain, "/clip/gain");
    
    

    def broadcast(self, msg):

        new_msg = []
        for i in range(2, len(msg)):
            new_msg.append(msg[i])
        
        self.oscServer.sendOSC(msg[0], new_msg)


    def changeGain(self, msg):
        

        track = msg[2]
        scene = msg[3]
        gain = msg[4]

        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]

        clip = clipSlot.clip
        gain_str = ''
        try:
            clip.gain = gain
            gain_str = repr2(clip.gain_display_string)
            self.oscServer.sendOSC("/clip/gain", (int(track), int(scene), gain_str))

        except:
            pass



    def toggleStopButton(self, msg):
        track = msg[2]
        scene = msg[3]

        has_stop_button = msg[4]
        
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.has_stop_button = int(has_stop_button)



    def loopInfo(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        clip = LiveUtils.getClip(trackNumber, clipNumber)

        looping = clip.looping
        loop_start = 0
        loop_end = 0
        start = 0
        end = 0
        
        if looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            clip.looping = 0
    
        
    def clipstuff(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]

        clip = LiveUtils.getClip(trackNumber, clipNumber)
        if clip != None:
            nm = clip.name
            pitch_coarse = 0
            pitch_fine = 0
            is_audio_clip = 0
            warping = 0
            gain = 2
            gain_str = ''

            if clip.is_audio_clip:
                pitch_coarse = LiveUtils.getClip(trackNumber, clipNumber).pitch_coarse
                pitch_fine = LiveUtils.getClip(trackNumber, clipNumber).pitch_fine
                warping = LiveUtils.getClip(trackNumber, clipNumber).warping
                is_audio_clip = 1;
                try:
                    gain = clip.gain
                    gain_str = clip.gain_display_string
                except:
                    pass

            if clip.looping:
                loop_start = clip.loop_start
                loop_end = clip.loop_end
                clip.looping = 0
                end = clip.loop_end
                start = clip.loop_start
                clip.looping = 1
            else:
                end = clip.loop_end
                start = clip.loop_start
                clip.looping = 1
                loop_start = clip.loop_start
                loop_end = clip.loop_end
                clip.looping = 0
            if clip.is_audio_clip:
                clip.warping = warping

            length = clip.length
            mute = clip.muted
            loop = clip.looping
            color = clip.color
            signature_denominator = clip.signature_denominator
            signature_numerator = clip.signature_numerator

            self.oscServer.sendOSC("/clipstuff", (int(trackNumber), int(clipNumber), repr2(nm), int(loop), int(mute), float(pitch_coarse), float(pitch_fine), float(start), float(end), float(length), int(color), int(is_audio_clip), int(signature_denominator), int(signature_numerator), int(warping), float(loop_start), float(loop_end), float(gain), repr2(gain_str)))


        else:
            nm = "aNo Clip selected"
            loop = 0
            mute = 0
            pitch = 0
            start = 0
            end = 0
            length = 0
            color = 0
            self.oscServer.sendOSC("/clipstuff", (int(trackNumber), int(clipNumber), repr2(nm), int(loop), int(mute), float(pitch), float(start), float(end), float(length), int(color)))


    def loopclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        looping = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).looping = looping

    def muteclipCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        muted = msg[4]
        LiveUtils.getClip(trackNumber, clipNumber).muted = muted
    

    def createClip(self, msg):
        track = msg[2]
        scene = msg[3]
        length = msg[4]
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.create_clip(float(length))
    
    def deleteClip(self, msg):
        track = msg[2]
        scene = msg[3]
        clipSlot = LiveUtils.getSong().tracks[track].clip_slots[scene]
        clipSlot.delete_clip()
    
    def duplicateClip(self, msg):
        track = msg[2]
        scene = msg[3]
        track = LiveUtils.getTrack(track)
        track.duplicate_clip_slot(scene)

    def deleteDevice(self, msg):
        
        type = msg[2]
        tid = msg[3]
        device_id = msg[4]
        
        number_of_steps = msg[5]
        
        if type == 0:
            track = LiveUtils.getSong().tracks[tid]

        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track

        device = track.devices[device_id]


        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            track = device.chains[chain_id]
            device = track.devices[device_id]


        track.delete_device(device_id)

    
    
    def deleteReturnDevice(self, msg):
        tr = msg[2]
        de = msg[3]
        track = LiveUtils.getSong().return_tracks[tr]
        track.delete_device(de)

    
    def deleteMasterDevice(self, msg):
        de = msg[2]
        track = LiveUtils.getSong().master_track
        track.delete_device(de)
    
    

        
    
    def duplicateTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().duplicate_track(track)
    
    def duplicateScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().duplicate_scene(scene)
    
    def createScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().create_scene(scene)
    
    def deleteScene(self, msg):
        scene = msg[2]
        LiveUtils.getSong().delete_scene(scene)
    
    def createMidiTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_midi_track(track)
    
    
    def createAudioTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_audio_track(track)
    
    
    def createReturnTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().create_return_track()

    
    def deleteTrack(self, msg):
        track = msg[2]
        LiveUtils.getSong().delete_track(track)
    
    def deleteReturn(self, msg):
        track = msg[2]
        LiveUtils.getSong().delete_return_track(track)

    def pitchcoarseCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        pitch = int(msg[4])
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        if clip.is_audio_clip == 1:
            clip.pitch_coarse = int(pitch)
        

    def detuneCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        pitch = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)

        if clip.is_audio_clip == 1:
            clip.pitch_fine = float(pitch)


    def startposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        start = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        #isWarping = clip.warping
        
        clip.looping = 1
        clip.loop_start = start
        clip.looping = isLoop
        #clip.warping = isWarping

    def endposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        end = msg[4]
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        #isWarping = clip.warping
        
        clip.looping = 1
        clip.loop_end = end
        clip.looping = isLoop
        #clip.warping = isWarping
    
    def clipstartposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        start = msg[4]
        
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        if clip.is_audio_clip:
            isWarping = clip.warping
        clip.looping = 0
        clip.loop_start = start
        clip.looping = isLoop
        
        if clip.is_audio_clip:
            clip.warping = isWarping
    
    def clipendposCB(self, msg):
        trackNumber = msg[2]
        clipNumber = msg[3]
        end = msg[4]
        
        clip = LiveUtils.getClip(trackNumber, clipNumber)
        isLoop = clip.looping
        if clip.is_audio_clip:
            isWarping = clip.warping
        clip.looping = 0
        clip.loop_end = end
        clip.looping = isLoop

        if clip.is_audio_clip:
            clip.warping = isWarping
        
        
    def sigCB(self, msg):
        """ Called when a /live/clip/signature message is recieved
        """
        track = msg[2]
        clip = msg[3]
        c = LiveUtils.getSong().tracks[track].clip_slots[clip].clip
        
        if len(msg) == 4:
            self.oscServer.sendOSC("/live/clip/signature", (track, clip, c.signature_numerator, c.signature_denominator))
            
        if len(msg) == 6:
            self.oscServer.sendOSC("/live/clip/signature", 1)
            c.signature_denominator = msg[5]
            c.signature_numerator = msg[4]


    def nudgeupCB(self, msg):
        onoff = msg[2]
        LiveUtils.getSong().nudge_up = onoff

    def nudgedownCB(self, msg):
        onoff = msg[2]
        LiveUtils.getSong().nudge_down = onoff


    def cuelevelCB(self, msg):
        if len(msg) == 2:
            value = LiveUtils.getSong().master_track.mixer_device.cue_volume.value
            self.oscServer.sendOSC("/set/cuelevel", float(value))
        elif len(msg) == 3:
            value = msg[2]
            LiveUtils.getSong().master_track.mixer_device.cue_volume.value = value
        
    def warpingCB(self, msg):
        """ Called when a /live/clip/warping message is recieved
        """
        track = msg[2]
        clip = msg[3]
        
        
        if len(msg) == 4:
            state = LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping
            self.oscServer.sendOSC("/live/clip/warping", (track, clip, int(state)))
        
        elif len(msg) == 5:
            LiveUtils.getSong().tracks[track].clip_slots[clip].clip.warping = msg[4]

    def selectionCB(self, msg):
        """ Called when a /live/selection message is received
        """
#        self.liveOSC.log_message( "*** SELECTION_CB: " + str( msg[ 2 ] ) + ", " + str( msg[ 3 ] ) + ", " + str( msg[ 4 ] ) + ", " + str( msg[ 5 ] )  )
#        self.c_instance.set_session_highlight(msg[2], msg[3], msg[4], msg[5], 0)
        self.touchAble.session.set_highlight(msg[2], msg[3], msg[4], msg[5])

        # LMH
        self.touchAble.session._set_lsync_offsets_from_touchable( msg[2], msg[3], msg[4], msg[5] )

    def abAssignCB(self, msg):
        tr = msg[2]
        val = msg[3]
        track = LiveUtils.getTrack(tr)
        oldVal = track.mixer_device.crossfade_assign
        if oldVal == val:
            track.mixer_device.crossfade_assign = 1
        else:
            track.mixer_device.crossfade_assign = val
                
    def returnabAssignCB(self, msg):
        tr = msg[2]
        val = msg[3]
        track = LiveUtils.getSong().return_tracks[tr]
        oldVal = track.mixer_device.crossfade_assign
        if oldVal == val:
            track.mixer_device.crossfade_assign = 1
        else:
            track.mixer_device.crossfade_assign = val
    
    def trackxfaderCB(self, msg):
        """ Called when a /live/track/crossfader or /live/return/crossfader message is received
        """
        ty = msg[0] == '/return/abAssign' and 1 or 0
    
        if len(msg) == 3:
            track = msg[2]
        
            if ty == 1:
                assign = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().return_tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscServer.sendOSC("/return/crossfader", (track, repr2(assign), repr2(name)))
            else:
                assign = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assign
                name   = LiveUtils.getSong().tracks[track].mixer_device.crossfade_assignments.values[assign]
            
                self.oscServer.sendOSC("/track/crossfader", (track, repr2(assign), repr2(name)))

            
        elif len(msg) == 4:
            track = msg[2]
            assign = msg[3]
            
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track]
                oldVal = track.mixer_device.crossfade_assign
                if oldVal == assign:
                    track.mixer_device.crossfade_assign = 1
                else:
                    track.mixer_device.crossfade_assign = assign
            else:
                track = LiveUtils.getSong().tracks[track]
                oldVal = track.mixer_device.crossfade_assign
                if oldVal == assign:
                    track.mixer_device.crossfade_assign = 1
                else:
                    track.mixer_device.crossfade_assign = assign

    def tempoCB(self, msg):
        """Called when a /live/tempo message is received.

        Messages:
        /live/tempo                 Request current tempo, replies with /live/tempo (float tempo)
        /live/tempo (float tempo)   Set the tempo, replies with /live/tempo (float tempo)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscServer.sendOSC("/set/tempo", LiveUtils.getTempo())
        
        elif len(msg) == 3:
            tempo = msg[2]
            LiveUtils.setTempo(tempo)
        
    def timeCB(self, msg):
        """Called when a /live/time message is received.

        Messages:
        /live/time                 Request current song time, replies with /live/time (float time)
        /live/time (float time)    Set the time , replies with /live/time (float time)
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscServer.sendOSC("/set/playing_position", float(LiveUtils.currentTime()))

        elif len(msg) == 3:
            time = msg[2]
            LiveUtils.currentTime(time)

    def nextCueCB(self, msg):
        """Called when a /live/next/cue message is received.

        Messages:
        /live/next/cue              Jumps to the next cue point
        """
        LiveUtils.jumpToNextCue()
        
    def prevCueCB(self, msg):
        """Called when a /live/prev/cue message is received.

        Messages:
        /live/prev/cue              Jumps to the previous cue point
        """
        LiveUtils.jumpToPrevCue()
        
    def playCB(self, msg):
        """Called when a /live/play message is received.

        Messages:
        /live/play              Starts the song playing
        """
        LiveUtils.play()
        
    def playContinueCB(self, msg):
        """Called when a /live/play/continue message is received.

        Messages:
        /live/play/continue     Continues playing the song from the current point
        """
        LiveUtils.continuePlaying()
        
    def playSelectionCB(self, msg):
        """Called when a /live/play/selection message is received.

        Messages:
        /live/play/selection    Plays the current selection
        """
        LiveUtils.playSelection()


    def playClipCB(self, msg):
        """Called when a /live/play/clip message is received.

        Messages:
        /live/play/clip     (int track, int clip)   Launches clip number clip in track number track
        """
        if len(msg) == 4:
            track = msg[2]
            clip = msg[3]
            LiveUtils.launchClip(track, clip)
           



    def foldTrackCB(self, msg):
        tr = msg[2]
        
        track = LiveUtils.getTrack(tr)
        if track.is_foldable == 1:
            if track.fold_state == 0:
                track.fold_state = 1
            else:
                track.fold_state = 0
        else:
            pass
        
    
    def playSceneCB(self, msg):
        """Called when a /live/play/scene message is received.

        Messages:
        /live/play/scene    (int scene)     Launches scene number scene
        """
        if len(msg) == 3:
            scene = msg[2]
            trackNumber = 0
            LiveUtils.launchScene(scene)
            #self.oscServer.sendOSC("/scene/fired", int(scene)+1)

            for track in LiveUtils.getTracks():
                if track.is_foldable != 1:
                    clipslot = track.clip_slots[scene]
                    if clipslot.clip == None:
                        if track.playing_slot_index != -2:
                            if track.playing_slot_index != -1:
                                if clipslot.has_stop_button == 1:
                                    self.oscServer.sendOSC('/clip/playing_status', (trackNumber, scene, 5))
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
                            
                trackNumber = trackNumber +1
                    


                
    
    def stopCB(self, msg):
        """Called when a /live/stop message is received.

        Messages:
        /live/stop              Stops playing the song
        """
        LiveUtils.stop()
        
    def stopClipCB(self, msg):
        """Called when a /live/stop/clip message is received.

        Messages:
        /live/stop/clip     (int track, int clip)   Stops clip number clip in track number track
        """
        if len(msg) == 4:
            track = msg[2]
            clip = msg[3]
            LiveUtils.stopClip(track, clip)

    def stopTrackCB(self, msg):
        """Called when a /live/stop/track message is received.

        Messages:
        /live/stop/track     (int track, int clip)   Stops track number track
        """
        
        i = msg[2]
        LiveUtils.stopTrack(i)
        track = LiveUtils.getTrack(i)
        if track.playing_slot_index != -2:
            if track.playing_slot_index != -1: 
                self.oscServer.sendOSC('/track/stop', (1, i))
            else:
                pass
        else:
            pass
            


    def stopAllCB(self, msg):
        """Called when a /live/stop/track message is received.

        Messages:
        /live/stop/track     (int track, int clip)   Stops track number track
        """
        if len(msg) == 2:
            LiveUtils.getSong().stop_all_clips()                    

    def scenesCB(self, msg):
        """Called when a /live/scenes message is received.

        Messages:
        /live/scenes        no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            sceneTotal = len(LiveUtils.getScenes())
            self.oscServer.sendOSC("/scenes", (sceneTotal))
            return

    def sceneCB(self, msg):
        """Called when a /live/scene message is received.
        
        Messages:
        /live/scene         no argument or 'query'  Returns the currently playing scene number
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            selected_scene = LiveUtils.getSong().view.selected_scene
            scenes = LiveUtils.getScenes()
            index = 0
            selected_index = 0
            for scene in scenes:
                index = index + 1        
                if scene == selected_scene:
                    selected_index = index
                    
            self.oscServer.sendOSC("/scene", (selected_index))
            
        elif len(msg) == 3:
            scene = msg[2]
            LiveUtils.getSong().view.selected_scene = LiveUtils.getSong().scenes[scene]

    def update(self, msg):
        self.oscServer.sendOSC("/bundle/start", 1)
        self.songtime_change()
        self.meters()
        self.mastermeters()
        self.positions()
        self.oscServer.sendOSC("/finish_loading", (1))
        self.oscServer.sendOSC("/bundle/end", (1))

    
    def songtime_change(self):
        self.oscServer.sendOSC("/set/playing_position", (LiveUtils.getSong().current_song_time + 0.0001))
    
    def meters(self):
        tracks = LiveUtils.getSong().tracks
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

            
            
    def mastermeters(self):
        tracks = LiveUtils.getSong().return_tracks
        vall = LiveUtils.getSong().master_track.output_meter_left
        valr = LiveUtils.getSong().master_track.output_meter_right
        
        vall = round(vall, 3)
        valr = round(valr, 3)
        
        if vall != self.mmcache:
            self.oscServer.sendOSC('/master/meter',(vall, valr))
            if vall == 0:
                self.oscServer.sendOSC('/master/meter',(0.0000000001))
            self.mmcache = vall
        i = 0
        for track in tracks:
            vall = track.output_meter_left
            valr = track.output_meter_right
            
            vall = round(vall, 3)
            valr = round(valr, 3)
            
            if vall != self.mrcache[i]:
                self.oscServer.sendOSC('/return/meter',(i, vall, valr))
                self.mrcache[i] = vall
            else:
                pass
            i = i+1
    
            
            
    def positions(self):
        tracks = LiveUtils.getSong().tracks
        pos = 0
        ps = 0
        if LiveUtils.getSong().is_playing != 4:
            for i in range(len(tracks)):
                track = tracks[i]
                if track.is_foldable != 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            ps = track.playing_slot_index
                            clip = track.clip_slots[ps].clip
                            if clip.looping == 1:
                                if clip.playing_position < clip.loop_start:
                                    clip.looping = 0
                                    start = clip.loop_start
                                    end = clip.loop_end
                                    clip.looping = 1
                                    pos = round((clip.playing_position - start) / (end - start), 6)
                                #pos = round((clip.loop_start - clip.playing_position) / (clip.loop_start - start), 3)
                                else:
                                    pos = round((clip.playing_position - clip.loop_start) / (clip.loop_end - clip.loop_start), 6)
                            
                            else:
                                pos = round((clip.playing_position-clip.loop_start) / (clip.length), 6)
                            
                            self.oscServer.sendOSC('/clip/playing_position',(i, ps, pos, clip.playing_position))
                        else:
                            pass
                    else:
                        pass
                
                else:
                    pass
        
        else:
            pass


    def loadAllCB(self, msg):
        """Called when a /live/tracks message is received.

        Messages:
        /live/tracks       no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            trackTotal = len(LiveUtils.getTracks())
            sceneTotal = len(LiveUtils.getScenes())
            returnsTotal = len(LiveUtils.getSong().return_tracks)
            self.oscServer.sendOSC("/set/size", (trackTotal, sceneTotal, returnsTotal))
            return

    def tracksCB(self, msg):
        load_browser = msg[2]
        
        
        c = Live.Application.get_application().get_bugfix_version()
        b = Live.Application.get_application().get_minor_version()
        a = Live.Application.get_application().get_major_version()
        self.oscServer.sendOSC("/live/version", (int(a), int(b), int(c)))


        self.oscServer.sendOSC("/bundle/start", 1)
               
        trackTotal = len(LiveUtils.getTracks())
        sceneTotal = len(LiveUtils.getScenes())
        returnsTotal = len(LiveUtils.getSong().return_tracks)
       
        #self.oscServer.udpClient.send(bundle.getBinary())
        #self.oscClient.send("/set/test" bundle)
        
        self.oscServer.sendOSC("/set/size", (int(trackTotal), int(sceneTotal), int(returnsTotal)))
        
        
        tquant = LiveUtils.getSong().clip_trigger_quantization
        rquant = LiveUtils.getSong().midi_recording_quantization
        self.oscServer.sendOSC("/set/quantization", (int(LiveUtils.getSong().clip_trigger_quantization), int(LiveUtils.getSong().midi_recording_quantization)))
        
        songtime = LiveUtils.getSong().current_song_time
        self.oscServer.sendOSC("/set/playing_position", (float(songtime) + 0.001))
        
        overdub = LiveUtils.getSong().overdub
        self.oscServer.sendOSC("/set/overdub_status", (int(overdub) + 1))
        
        record = LiveUtils.getSong().record_mode
        self.oscServer.sendOSC("/set/recording_status", (int(record) + 1))
        
        
        
        try:
            overdub = LiveUtils.getSong().session_record
            self.oscServer.sendOSC("/live/set/session_record", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().session_record_status
            self.oscServer.sendOSC("/live/set/session_record_status", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().re_enable_automation_enabled
            self.oscServer.sendOSC("/live/set/re_enable_automation_enabled", (int(overdub)+1))
        
            overdub = LiveUtils.getSong().session_automation_record
            self.oscServer.sendOSC("/live/set/session_automation_record", (int(overdub)+1))
        except:
            self.oscServer.sendOSC("/live/", 8)

        
        
        tempo = LiveUtils.getTempo()
        self.oscServer.sendOSC("/set/tempo", (tempo))
            
        value = LiveUtils.getSong().master_track.mixer_device.cue_volume.value
        self.oscServer.sendOSC("/cuelevel", float(value))
        
        metronome = LiveUtils.getSong().metronome
        self.oscServer.sendOSC("/set/metronome_status", (int(metronome) + 1))
        
        play = LiveUtils.getSong().is_playing
        self.oscServer.sendOSC("/set/playing_status", (int(play) + 1))
        
        master = LiveUtils.getSong().master_track.mixer_device.volume.value
        self.oscServer.sendOSC("/master/volume", (float(master)))
        
        crossfader = LiveUtils.getSong().master_track.mixer_device.crossfader.value
        self.oscServer.sendOSC("/master/crossfader", float(crossfader))
                
        selected_track = LiveUtils.getSong().view.selected_track
        selected_index = 0

        selected_scene = LiveUtils.getSong().view.selected_scene
        
        scene_index = 0
        selected_scene_index = 0
        for sce in LiveUtils.getSong().scenes:
            if sce == selected_scene:
                selected_scene_index = scene_index
            scene_index = scene_index + 1
        
        
        self.oscServer.sendOSC("/set/selected_scene", int(selected_scene_index+1))


        trackNumber = 0
        ascnm = " "
        nm = " "
        grouptrack = 0
        is_midi_track = 0
        for track in LiveUtils.getTracks():
            clipNumber = 0
            if track.name != None:
                nm = cut_string2(track.name)
                col = 0
                try:
                    col = track.color
                except:
                    pass
            if track.is_foldable == 1:
                grouptrack = 1
            else:
                grouptrack = 0
            is_midi_track = track.has_midi_input
        
            self.oscServer.sendOSC("/track", (trackNumber, repr2(nm), col, grouptrack, int(is_midi_track)))
            self.oscServer.sendOSC("/track/volume", (trackNumber, float(LiveUtils.trackVolume(trackNumber))))
            self.oscServer.sendOSC("/pan", (trackNumber, float(LiveUtils.trackPan(trackNumber))))
            self.oscServer.sendOSC("/track/mute", (trackNumber, int(track.mute)))
            self.oscServer.sendOSC("/track/solo", (trackNumber, int(track.solo)))
            self.oscServer.sendOSC("/track/crossfade_assign", (trackNumber, int(track.mixer_device.crossfade_assign)))
            self.oscServer.sendOSC("/track/is_visible", (trackNumber, int(track.is_visible)))
        
        
        
        
            for clipSlot in track.clip_slots:
                if clipSlot.clip != None:
                    play = 0
                    clip = clipSlot.clip
                    if clip.is_playing == 1:
                        play = 1
                    elif clip.is_triggered == 1:
                        play = 2
                    elif clip.is_recording == 1:
                        play = 3
                    if clip.name != None:
                        nm = cut_string2(clip.name)
                    #ascnm = nm.encode('ascii', 'replace')
                    else:
                        nm = " "
                    
                    self.oscServer.sendOSC("/clip", (trackNumber, clipNumber, repr2(nm), clip.color, play))



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
                        
                    start = clip.loop_start
                    end = clip.loop_end
                   
                    self.oscServer.sendOSC('/clip/loopstats', (trackNumber, clipNumber, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
                        
                else:
                    play = 0
                    if clipSlot.has_stop_button == 1:
                        if track.is_foldable != 1:
                            self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"stop", 2500134, play))
                            self.oscServer.sendOSC("/clipslot/stop", (trackNumber, clipNumber))
                        else:
                            nextClipSlot = LiveUtils.getTrack(trackNumber+1).clip_slots[clipNumber]
                            if nextClipSlot.clip != None:
                                nextClip = nextClipSlot.clip
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12V3", nextClip.color, play))
                            else:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12V3", 12632256, play))

                    else:
                        if track.is_foldable != 1:
                            self.oscServer.sendOSC("/clipslot/empty", (trackNumber, clipNumber))
                        
                        else:
                            if track.fold_state == 1:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12V3", 3289650, play))
                            else:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12>3", 3289650, play))
                
                clipNumber = clipNumber + 1
        

        
            if track.can_be_armed == 1:
                self.oscServer.sendOSC("/track/arm", (trackNumber, int(track.arm)))
                self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, track.current_monitoring_state))

            else:
                self.oscServer.sendOSC("/track/arm", (trackNumber, 0))
                self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, 3))

                
                    
            self.load_devices_for_track(track, trackNumber, 0)


            
            for i in range(len(LiveUtils.getSong().return_tracks)):
                self.oscServer.sendOSC("/track/send", (trackNumber,i, float(LiveUtils.trackSend(trackNumber, i))))

                    
            if track == selected_track:
                selected_index = trackNumber
                self.oscServer.sendOSC("/set/selected_track", (0, (selected_index)))

            trackNumber = trackNumber + 1
            #time.sleep(0.05)
                
       
        returnNumber = 0
        returnsTotal = len(LiveUtils.getSong().return_tracks)
        self.oscServer.sendOSC("/returns", (int(returnsTotal), 1))
        
        for retTrack in LiveUtils.getSong().return_tracks:
            name = retTrack.name
            color = 0
            try:
                color = retTrack.color
            except:
                pass

            self.oscServer.sendOSC("/return", (int(returnNumber), repr2(name), int(color)))
            self.oscServer.sendOSC("/return/pan", (returnNumber, float(retTrack.mixer_device.panning.value)))
            self.oscServer.sendOSC("/return/mute", (returnNumber, int(retTrack.mute)))
            self.oscServer.sendOSC("/return/crossfade_assign", (returnNumber, int(retTrack.mixer_device.crossfade_assign)))
            self.oscServer.sendOSC("/return/solo", (returnNumber, int(retTrack.solo)))
            self.oscServer.sendOSC("/return/volume", (returnNumber, float(retTrack.mixer_device.volume.value)))


            self.load_devices_for_track(retTrack, int(returnNumber), int(2))



            for i in range(len(LiveUtils.getSong().return_tracks)):
                self.oscServer.sendOSC("/return/send", (returnNumber,i, float(retTrack.mixer_device.sends[i].value)))
        
            
            if retTrack == selected_track:
                selected_index = returnNumber
                self.oscServer.sendOSC("/set/selected_track", (2, (selected_index)))
                
            returnNumber = returnNumber + 1

        sceneNumber = 0
        ascnm = " "
        nm = " "
        
        self.load_devices_for_track(LiveUtils.getSong().master_track, int(1), int(1))


        if LiveUtils.getSong().master_track == selected_track:
            self.oscServer.sendOSC("/set/selected_track", (1))

        
        for scene in LiveUtils.getScenes():
            nm = ""
            if scene.name != None:
                nm = cut_string2(scene.name)
            if scene.color == 0:
                self.oscServer.sendOSC("/scene", (sceneNumber, repr2(nm), 0))
            else:
                self.oscServer.sendOSC("/scene", (sceneNumber, repr2(nm), scene.color))
                    
            sceneNumber = sceneNumber + 1

        
        if load_browser == 1:
            self.oscServer.sendOSC("/browser/load_browser_1", 1)
            if a >= 9:
                self.oscServer.sendOSC("/browser/live_9", 1)

                try:
                    self.oscServer.sendOSC("/browser/starting", 1)
                    self.getBrowserItems()
                except:
                    self.oscServer.sendOSC("/browser/except", 1)
                    pass
            else:
                self.oscServer.sendOSC("/browser/live_not_9", 1)
        else:
            self.oscServer.sendOSC("/browser/load_browser_0", 1)


        self.oscServer.sendOSC("/track/update_state", (1))
        self.oscServer.sendOSC("/browser/end", 1)
        self.oscServer.sendOSC("/done", (1))

        self.oscServer.sendOSC("/finish_loading", (1))
        self.oscServer.sendOSC("/bundle/end", (1))
            


    
    def getBrowserItems(self):
        self.oscServer.sendOSC("/browser/getting_browser", 1)

        browser = Live.Application.get_application().browser
        self.oscServer.sendOSC("/browser/got_browser", 1)
        self.oscServer.sendOSC("/NSLOG_REPLACE", str("GOT BROWSER"))

        dir(browser)
        
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
        
        self.oscServer.sendOSC("/browser/got_root_items", 1)


        steps = 1
        i = 0

        self.oscServer.sendOSC("/browser/start", 1)

    
        for item in root_items:
    

            is_folder = 1
            
            count = len(item.children)

            indis = [repr2(item.name), int(steps), int(item.is_loadable), int(count)]
            indis.append(int(i))
            
            self.oscServer.sendOSC("/browser/item", tuple(indis))
            i = i+1


        """obj = list(browser.user_folders)
        count = len(obj)
        indis = ["User folder", int(steps), int(0), int(count)]
        indis.append(int(i))
        self.oscServer.sendOSC("/browser/item", tuple(indis))
        
        
        i = i+1
        a_version = Live.Application.get_application().get_major_version()
        
        if a_version >= 10:
            obj = list(browser.colors)
            count = len(obj)
            indis = ["Collections", int(steps), int(0), int(count)]
            indis.append(int(i))
        self.oscServer.sendOSC("/browser/item", tuple(indis))"""
    
    
    def loadChildren(self, msg):
        
        steps = msg[2]
        browser = Live.Application.get_application().browser
        
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
        
        ind = msg[3]
        
        #message = " length root items " + str(len(root_items)) + " index "  + str(ind)
        #self.oscServer.sendOSC("/NSLOG_REPLACE", message)
        
        if ind >= len(root_items):
            indexInPlaces = ind - len(root_items)
            if ind == 11:
                item = list(browser.user_folders)
            if ind == 12:
                item = list(browser.colors)
        
            indices = [msg[3]]
            
            for i in range(steps-1):
                index = msg[4+i]
                item = item[index]
                indices.append(int(index))
    
            j = 0
        
            if steps < 2:
            
                c = len(item)
                itemIndis = [steps]
                itemIndis.append(int(c))
                for index in indices:
                    itemIndis.append(int(index))
                
                for i in range(len(item)):
                    subItem = item[i]
                    count = (len(subItem.children))
                    indis = [repr2(subItem.name), int(steps+1), int(1), int(count)]
                    for index in indices:
                        indis.append(int(index))
                    indis.append(int(j))
                    self.oscServer.sendOSC("/browser/item", tuple(indis))
                    j = j+1
            else:
                
                c = len(item.children)
                itemIndis = [steps]
                itemIndis.append(int(c))
                for index in indices:
                    itemIndis.append(int(index))
                
                
                for subItem in item.children:
                    count = len(subItem.children)
                    indis = [repr2(subItem.name), int(steps+1), int(subItem.is_loadable), int(count)]
                    for index in indices:
                        indis.append(int(index))
                    indis.append(int(j))
                    self.oscServer.sendOSC("/browser/item", tuple(indis))
                    j = j+1
    
        
            self.oscServer.sendOSC("/browser/children_loaded", tuple(itemIndis))
        
        else:
            
            item = root_items[msg[3]]
            
            
            indices = [msg[3]]
            
            for i in range(steps-1):
                index = msg[4+i]
                item = item.children[index]
                indices.append(int(index))
            
            
            c = len(item.children)
            itemIndis = [steps]
            itemIndis.append(int(c))
            for index in indices:
                itemIndis.append(int(index))
            
            
            j = 0
            #self.oscServer.sendOSC("/bundle/start", (1))
            
            for subItem in item.children:
                count = len(subItem.children)
                indis = [repr2(subItem.name), int(steps+1), int(subItem.is_loadable), int(count)]
                for index in indices:
                    indis.append(int(index))
                indis.append(int(j))
                
                self.oscServer.sendOSC("/browser/item", tuple(indis))
                j = j+1
            self.oscServer.sendOSC("/browser/children_loaded", tuple(itemIndis))
        #self.oscServer.sendOSC("/bundle/end", (1))
            


    def getBrowserRoot(self):
        
        browser = Live.Application.get_application().browser
        
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
        self.oscServer.sendOSC("/browser/start", 1)
        
        
        for item in root_items:
            
            lis = list(indices)
            
            self.getChildren(item, steps, lis, i)
            
            i = i+1
        
        
        self.oscServer.sendOSC("/browser/end", 1)


    def getChildren(self, item, steps, indices, i):
        is_folder = 0
        if len(item.children)>0:
            is_folder = 1
        
        count = len(item.children)
        
        indices.append(int(i))
        indis = [repr2(item.name), int(steps), int(item.is_loadable), int(count)]
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




    def activateLoopCB(self, msg):
    
        tr = msg[2]
        cl = msg[3]
        length = msg[4]
        clip = LiveUtils.getClip(tr, cl)
    
        clip.looping = 1
        clip.loop_end = round(clip.playing_position, 0) + length
        clip.loop_start = round(clip.playing_position, 0)
        
        
        if clip.loop_end > clip.loop_start + length:
            clip.loop_end = clip.loop_start + length
        else:
            pass
        
        if clip.loop_end < clip.loop_start + length:
            clip.loop_end = clip.loop_start + length
        else:
            pass

        is_audio_clip = int(clip.is_audio_clip)
        
        isLooping = int(clip.looping)
        
        warp = 0
        start = 0
        end = 0
        loop_start = 0
        loop_end = 0
            
        if is_audio_clip == 1:
            warp = int(clip.warping)
        else:
            pass
        
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
        
        if is_audio_clip == 1:
            clip.warping = warp
        else:
            pass
        
        clip.looping = isLooping
        
        self.oscServer.sendOSC('/clip/loopstats', (tr, cl, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
        

        
    def deactivateLoopCB(self, msg):
        tr = msg[2]
        cl = msg[3]
        clip = LiveUtils.getClip(tr, cl)
            
        clip.looping = 0
        
        is_audio_clip = int(clip.is_audio_clip)
        
        isLooping = int(clip.looping)
        is_audio_clip = int(clip.is_audio_clip)
        
        warp = 0
        start = 0
        end = 0
        loop_start = 0
        loop_end = 0
        
        if is_audio_clip == 1:
            warp = int(clip.warping)
        else:
            pass
        
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
        
        if is_audio_clip == 1:
            clip.warping = warp
        else:
            pass
        
        clip.looping = isLooping
        
        self.oscServer.sendOSC('/clip/loopstats', (tr, cl, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))


            

    def returnsCB(self, msg):
        """Called when a /live/returns message is received.

        Messages:
        /live/returns       no argument or 'query'  Returns the total number of scenes

        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            returnsTotal = len(LiveUtils.getSong().return_tracks)
            self.oscServer.sendOSC("/returns", (int(returnsTotal), 1))
            for i in range(len(LiveUtils.getSong().return_tracks)):
                name = LiveUtils.getSong().return_tracks[i].name
                color = 0
                try:
                    color = LiveUtils.getSong().return_tracks[i].color
                except:
                    pass
                
                self.oscServer.sendOSC("/return", (int(i), repr2(name), int(color)))
            return        


    def nameSceneCB(self, msg):
        """Called when a /live/name/scene message is received.

        Messages:
        /live/name/scene                            Returns a a series of all the scene names in the form /live/name/scene (int scene, string name)
        /live/name/scene    (int scene)             Returns a single scene's name in the form /live/name/scene (int scene, string name)
        /live/name/scene    (int scene, string name)Sets scene number scene's name to name

        """        
        #Requesting all scene names
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            sceneNumber = 0
            ascnm = " "
            nm = " "
            for scene in LiveUtils.getScenes():
                nm = ""
                if scene.name != None:
                    nm = cut_string2(scene.name)
                    #ascnm = (nm.encode('ascii', 'replace'))
                if scene.color == 0:
                    self.oscServer.sendOSC("/scene", (sceneNumber, repr2(nm), 0))
                else:
                    self.oscServer.sendOSC("/scene", (sceneNumber, repr2(nm), scene.color))
                
                sceneNumber = sceneNumber + 1
            return
        #Requesting a single scene name
        if len(msg) == 3:
            sceneNumber = msg[2]
            self.oscServer.sendOSC("/scene", (sceneNumber, repr2(LiveUtils.getScene(sceneNumber).name)))
            return
        #renaming a scene
        if len(msg) == 4:
            sceneNumber = msg[2]
            name = msg[3]
            LiveUtils.getScene(sceneNumber).name = name

            
            
    def nameTrackCB(self, msg):
        """Called when a /live/name/track message is received.

        Messages:
        /live/name/track                            Returns a a series of all the track names in the form /live/name/track (int track, string name)
        /live/name/track    (int track)             Returns a single track's name in the form /live/name/track (int track, string name)
        /live/name/track    (int track, string name)Sets track number track's name to name

        """        
        #Requesting all track names
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            ascnm = " "
            nm = " "
            grouptrack = 0
            for track in LiveUtils.getTracks():
                if track.name != None:
                    nm = cut_string2(track.name)
                    col = 0
                    try:
                        col = track.color
                    except:
                        pass
                    if track.is_foldable == 1:
                        grouptrack = 1
                    else:
                        grouptrack = 0
                #ascnm = (nm.encode('ascii', 'replace'))
                self.oscServer.sendOSC("/track", (trackNumber, repr2(nm), col, grouptrack))
                
                trackNumber = trackNumber + 1
            return
        #Requesting a single track name
        if len(msg) == 3:
            trackNumber = msg[2]
            self.oscServer.sendOSC("/track", (trackNumber, repr2(LiveUtils.getTrack(trackNumber).name)))
            return
        #renaming a track
        if len(msg) == 4:
            trackNumber = msg[2]
            name = msg[3]
            LiveUtils.getTrack(trackNumber).name = name

    def nameTrackBlockCB(self, msg):
        """Called when a /live/name/trackblock message is received.

        /live/name/trackblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([repr2(LiveUtils.getTrack(trackOffset+track).name)])
            self.oscServer.sendOSC("/trackblock", block)
    def doneCB(self, msg):
        self.oscServer.sendOSC("/done", 1)
    def nameSceneBlockCB(self, msg):
        """Called when a /live/name/sceneblock message is received.

        /live/name/sceneblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            sceneOffset = msg[2]
            blocksize = msg[3]
            for scene in range(0, blocksize):
                block.extend([repr2(LiveUtils.getScene(sceneOffset+scene).name)])
            self.oscServer.sendOSC("/sceneblock", block)            
            
    def volumeBlockCB(self, msg):
        """Called when a /volumeblock message is received.

        /live/volumeblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([float(LiveUtils.trackVolume(trackOffset+track))])
            self.oscServer.sendOSC("/volumeblock", block)

    def panBlockCB(self, msg):
        """Called when a /live/panblock message is received.

        /live/panblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([float(LiveUtils.trackPan(trackOffset+track))])
            self.oscServer.sendOSC("/panblock", block)            

    def sendaBlockCB(self, msg):
        """Called when a /live/sendablock message is received.

        /live/sendblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([float(LiveUtils.trackSend(trackOffset+track, 0))])               
            self.oscServer.sendOSC("/sendablock", block)

    def sendbBlockCB(self, msg):
        """Called when a /live/sendablock message is received.

        /live/sendblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):            
                block.extend([float(LiveUtils.trackSend(trackOffset+track, 1))])               
            self.oscServer.sendOSC("/sendbblock", block)            


    def sendcBlockCB(self, msg):
        """Called when a /live/sendablock message is received.

        /live/sendclock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):               
                block.extend([float(LiveUtils.trackSend(trackOffset+track, 2))])
            self.oscServer.sendOSC("/sendcblock", block)

    def senddBlockCB(self, msg):
        """Called when a /live/sendablock message is received.

        /live/senddblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([float(LiveUtils.trackSend(trackOffset+track, 3))])
            self.oscServer.sendOSC("/senddblock", block)

    def arms(self, msg):
        """Called when a /arms message is received.
        """        
        #Requesting all arms
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                if track.can_be_armed == 1:
                    self.oscServer.sendOSC("/track/arm", (trackNumber, int(track.arm)))
                else:
                    self.oscServer.sendOSC("/track/arm", (trackNumber, 0))

                
                trackNumber = trackNumber + 1
                

    def solos(self, msg):
        """Called when a /solos message is received.
        """        
        #Requesting all solos
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/track/solo", (trackNumber, int(track.solo)))
                
                trackNumber = trackNumber + 1
                
    def mutes(self, msg):
        """Called when a /mutes message is received.
        """        
        #Requesting all mutes
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/track/mute", (trackNumber, int(track.mute)))
                
                trackNumber = trackNumber + 1
           
            trackNumber = 0
            for track in LiveUtils.getSong().return_tracks:
                self.oscServer.sendOSC("/return/mute", (trackNumber, int(track.mute)))
        
                trackNumber = trackNumber + 1
    
    def abAssigns(self, msg):
        """Called when a /mutes message is received.
            """        
        #Requesting all A/B Assignments
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/track/crossfade_assign", (trackNumber, int(track.mixer_device.crossfade_assign)))
                
                trackNumber = trackNumber + 1
            
            
            trackNumber = 0
            for track in LiveUtils.getSong().return_tracks:
                self.oscServer.sendOSC("/return/crossfade_assign", (trackNumber, int(track.mixer_device.crossfade_assign)))
                
                trackNumber = trackNumber + 1
    
                
    def volumes(self, msg):
        """Called when a /volumes message is received.
        """        
        #Requesting all volumes
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/track/volume", (trackNumber, float(LiveUtils.trackVolume(trackNumber))))
                
                trackNumber = trackNumber + 1

    def sendas(self, msg):
        """Called when a /sendas message is received.
        """        
        #Requesting all sendas
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                for i in range(len(LiveUtils.getSong().return_tracks)):
                    self.oscServer.sendOSC("/track/send", (trackNumber,i, float(LiveUtils.trackSend(trackNumber, i))))
    
                trackNumber = trackNumber + 1
            trackNumber = 0
            for track in LiveUtils.getSong().return_tracks:
                for i in range(len(LiveUtils.getSong().return_tracks)):
                    self.oscServer.sendOSC("/return/send", (trackNumber,i, float(track.mixer_device.sends[i].value)))
            
                trackNumber = trackNumber + 1

    def sendbs(self, msg):
        """Called when a /sendbs message is received.
        """        
        #Requesting all sendbs
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/send", (trackNumber,1, float(LiveUtils.trackSend(trackNumber, 1))))
                
                trackNumber = trackNumber + 1
                
    def sendcs(self, msg):
        """Called when a /sendcs message is received.
        """        
        #Requesting all sendcs
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/send", (trackNumber,2, float(LiveUtils.trackSend(trackNumber, 2))))
                
                trackNumber = trackNumber + 1

    def sendds(self, msg):
        """Called when a /sendds message is received.
        """        
        #Requesting all sendds
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/send", (trackNumber, 3, float(LiveUtils.trackSend(trackNumber, 3))))
                
                trackNumber = trackNumber + 1

    def monitors(self, msg):
        """Called when a /monitors message is received.
        """        
        #Requesting all monitors
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                if LiveUtils.getTrack(trackNumber).can_be_armed == 1:
                    self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, int(LiveUtils.getTrack(trackNumber).current_monitoring_state)))
                else:
                    self.oscServer.sendOSC("/track/current_monitoring_state", (trackNumber, 3))
                
                trackNumber = trackNumber + 1
    
    def pans(self, msg):
        """Called when a /pans message is received.
        """        
        #Requesting all pans
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            trackNumber = 0
            for track in LiveUtils.getTracks():
                self.oscServer.sendOSC("/pan", (trackNumber, float(LiveUtils.trackPan(trackNumber))))
                
                trackNumber = trackNumber + 1
            trackNumber = 0
            for track in LiveUtils.getSong().return_tracks:
                self.oscServer.sendOSC("/return/pan", (trackNumber, float(track.mixer_device.panning.value)))
                
                trackNumber = trackNumber + 1

            
    def armblockCB(self, msg):                                                                                                                                        
        """Called when a /live/name/armblock message is received.

        /live/name/armblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:     
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):                
                block.extend([int(LiveUtils.getTrack(trackOffset+track).arm)])
            self.oscServer.sendOSC("/armblock", block)

    def muteblockCB(self, msg): 
        """Called when a /live/name/muteblock message is received.

        /live/name/muteblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize): 
                block.extend([int(LiveUtils.getTrack(trackOffset+track).mute)])
            self.oscServer.sendOSC("/muteblock", block)

    def monitorBlockCB(self, msg): 
        """Called when a /live/name/monitorblock message is received.

        /live/name/monitorblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                if LiveUtils.getTrack(trackOffset+track).can_be_armed == 1:
                    block.extend([int(LiveUtils.getTrack(trackOffset+track).current_monitoring_state)])
                else:
                    block.extend([3])

            self.oscServer.sendOSC("/monitorblock", block)

    def soloblockCB(self, msg):
        """Called when a /live/name/soloblock message is received.

        /live/name/soloblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            block = []
            trackOffset = msg[2]
            blocksize = msg[3]
            for track in range(0, blocksize):
                block.extend([int(LiveUtils.getTrack(trackOffset+track).solo)])
            self.oscServer.sendOSC("/soloblock", block)
 


    def nameClipBlockCB(self, msg):
        """Called when a /live/name/clipblock message is received.

        /live/name/clipblock    (int track, int clip, blocksize x/tracks, blocksize y/clipslots) Returns a list of clip names for a block of clips (int blockX, int blockY, clipname)

        """
        #Requesting a block of clip names X1 Y1 X2 Y2 where X1,Y1 is the first clip (track, clip) of the block, X2 the number of tracks to cover and Y2 the number of scenes
        
        if len(msg) == 6:
            block = []
            trackOffset = msg[2]
            clipOffset = msg[3]
            blocksizeX = msg[4]
            blocksizeY = msg[5]
            for track in range(0, blocksizeX):
                for clip in range(0, blocksizeY):
                    trackNumber = trackOffset+track                   
                    clipNumber = clipOffset+clip
                    if LiveUtils.getClip(trackNumber, clipNumber) != None:
                        block.extend([repr2(LiveUtils.getClip(trackNumber, clipNumber).name)])
                    else:
                        block.extend([""])                            
            self.oscServer.sendOSC("/nameblock", block)



    def clipplayBlockCB(self, msg):
        """Called when a /live/clipinfoblock message is received.

        /live/clipinfoblock    (int track, int clip, blocksize x/tracks, blocksize y/clipslots) Returns a list of clips playing statuses for a block of clips (int blockX, int blockY, clipname)

        """
        #Requesting a block of clip names X1 Y1 X2 Y2 where X1,Y1 is the first clip (track, clip) of the block, X2 the number of tracks to cover and Y2 the number of scenes
        
        if len(msg) == 6:
            block = []
            trackOffset = msg[2]
            clipOffset = msg[3]
            blocksizeX = msg[4]
            blocksizeY = msg[5]
            for track in range(0, blocksizeX):
                for clip in range(0, blocksizeY):
                        trackNumber = trackOffset+track
                        clipNumber = clipOffset+clip
                        if LiveUtils.getClip(trackNumber, clipNumber) != None:
                            if LiveUtils.getClip(trackNumber, clipNumber).is_playing == 1:
                                block.extend([1])
                            elif LiveUtils.getClip(trackNumber, clipNumber).is_triggered == 1:
                                block.extend([2])
                            else:
                                block.extend([0])
                        else:
                            block.extend([0])
                            
            self.oscServer.sendOSC("/playing", block)
           

    def nameColorBlockCB(self, msg):
        """Called when a /live/name/colorblock message is received.

        /live/name/clipblock    (int track, int clip, blocksize x/tracks, blocksize y/clipslots) Returns a list of clip colors for a block of clips (int blockX, int blockY, clipcolor)

        """
        #Requesting a block of clip colors X1 Y1 X2 Y2 where X1,Y1 is the first clip (track, clip) of the block, X2 the number of tracks to cover and Y2 the number of scenes
        
        if len(msg) == 6:
            block = []
            trackOffset = msg[2]
            clipOffset = msg[3]
            blocksizeX = msg[4]
            blocksizeY = msg[5]
            for track in range(0, blocksizeX):
                for clip in range(0, blocksizeY):
                        trackNumber = trackOffset+track
                        clipNumber = clipOffset+clip
                        if LiveUtils.getClip(trackNumber, clipNumber) != None:
                            block.extend([int(LiveUtils.getClip(trackNumber, clipNumber).color)])
                        else:
                            block.extend([0])
                            
            self.oscServer.sendOSC("/colorblock", block)



    def nameClipCB(self, msg):
        """Called when a /live/name/clip message is received.

        Messages:
        /live/name/clip                                      Returns a a series of all the clip names in the form /live/name/clip (int track, int clip, string name)
        /live/name/clip    (int track, int clip)             Returns a single clip's name in the form /live/name/clip (int clip, string name)
        /live/name/clip    (int track, int clip, string name)Sets clip number clip in track number track's name to name

        """
        
        #Requesting all clip names
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.1)
            trackNumber = 0
            clipNumber = 0
            countNumber = 0
            nm = " "
            ascnm = "-"
            for track in LiveUtils.getTracks():
                for clipSlot in track.clip_slots:
                    if clipSlot.clip != None:
                        play = 0
                        if clipSlot.clip.is_playing == 1:
                            play = 1
                        elif clipSlot.clip.is_triggered == 1:
                            play = 2
                        elif clipSlot.clip.is_recording == 1:
                            play = 3
                        if clipSlot.clip.name != None:
                            nm = cut_string2(clipSlot.clip.name)
                            #ascnm = nm.encode('ascii', 'replace')
                        else:
                            nm = " "

                        self.oscServer.sendOSC("/clip", (trackNumber, clipNumber, repr2(nm), clipSlot.clip.color, play))
                        self.clip_loopstats(clipSlot.clip, trackNumber, clipNumber)
                    else:
                        play = 0
                        if clipSlot.has_stop_button == 1:
                            if LiveUtils.getSong().tracks[trackNumber].is_foldable != 1:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"stop", 2500134, play))
                                self.oscServer.sendOSC("/clipslot/stop", (trackNumber, clipNumber))
                            else:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12>>3", 3289650, play))
                                
                        else:
                            if LiveUtils.getSong().tracks[trackNumber].is_foldable != 1:   
                                self.oscServer.sendOSC("/clipslot/empty", (trackNumber, clipNumber))

                            else:
                                self.oscServer.sendOSC("/clip", (trackNumber, clipNumber,"12>>3", 3289650, play))
                                
                    clipNumber = clipNumber + 1
                    countNumber = countNumber +1
                    if countNumber > 50:
                        #time.sleep(0.02)
                        countNumber = 0
                    else:
                        pass
                clipNumber = 0
                trackNumber = trackNumber + 1
            self.done()
            return
        #Requesting a single clip name
        if len(msg) == 4:
            trackNumber = msg[2]
            clipNumber = msg[3]
            self.oscServer.sendOSC("/clip", (trackNumber, clipNumber, repr2(LiveUtils.getClip(trackNumber, clipNumber).name), LiveUtils.getClip(trackNumber, clipNumber).color))
            return
        #renaming a clip
        if len(msg) == 5:
            trackNumber = msg[2]
            clipNumber = msg[3]
            name = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).name = name

    def clip_loopstats(self, clip, tid, cid):
        
        clip = LiveUtils.getClip(tid, cid)
        #isLooping = int(clip.looping)
        is_audio_clip = int(clip.is_audio_clip)

        warp = 0
        if is_audio_clip == 1:
            warp = int(clip.warping)
        else:
            pass
                
        if clip.looping == 1:
            loop_start = clip.loop_start
            loop_end = clip.loop_end
            
            #clip.looping = int(0)
            start = clip.loop_start
            end = clip.loop_end
        else:
            start = clip.loop_start
            end = clip.loop_end

            #clip.looping = 1
            loop_start = clip.loop_start
            loop_end = clip.loop_end
                
            
        #clip.looping = isLooping
       
        self.oscServer.sendOSC('/clip/loopstats', (tid, cid, isLooping, start, end, loop_start, loop_end, is_audio_clip, int(warp)))
        

    def done(self):
        #time.sleep(0.1)
        self.oscServer.sendOSC("/done", 1)
    
    def armTrackCB(self, msg):
        """Called when a /live/arm message is received.

        Messages:
        /live/arm     (int track)   (int armed/disarmed)     Arms track number track
        """
        track = msg[2]
        
        if len(msg) == 4:
            trk = LiveUtils.getTrack(track)
            if trk.can_be_armed:
                if msg[3] == 1:
                    status = LiveUtils.getTrack(track).arm

                    if LiveUtils.getSong().exclusive_arm == 1:
                        i = 0
                        for tr in LiveUtils.getTracks():
                            if tr.can_be_armed:
                                LiveUtils.disarmTrack(i)
                            else:
                                pass
                            i = i+1
                    
                    if status == 1:
                        LiveUtils.disarmTrack(track)
                    elif status == 0:
                        LiveUtils.armTrack(track)
                else:
                    LiveUtils.disarmTrack(track)
            else:
                pass
        # Return arm status
        elif len(msg) == 3:
            status = LiveUtils.getTrack(track).arm
            self.oscServer.sendOSC("/arm", (track, int(status)))     
            
    def muteTrackCB(self, msg):
        """Called when a /live/mute message is received.

        Messages:
        /live/mute     (int track)   Mutes track number track
        """
        ty = msg[0] == '/live/return/mute' and 1 or 0
        track = msg[2]
            
        if len(msg) == 4:
            if msg[3] == 1:
                if ty == 1:
                    status = LiveUtils.getSong().return_tracks[track].mute
                else:
                    status = LiveUtils.getTrack(track).mute
                if status == 1:
                    LiveUtils.unmuteTrack(track, ty)
                elif status == 0:        
                    LiveUtils.muteTrack(track, ty)
            else:
                LiveUtils.unmuteTrack(track, ty)
                
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].mute
                self.oscServer.sendOSC("/return/mute", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).mute
                self.oscServer.sendOSC("/mute", (track, int(status)))


    def monitorTrackCB(self, msg):
        """Called when a /live/monitor message is received.

        Messages:
        /live/monitor     (int track)   monitors track number track
        """
        track = msg[2]
            
        if len(msg) == 4:
            if LiveUtils.getTrack(track).current_monitoring_state == 0:
                LiveUtils.getTrack(track).current_monitoring_state = 1
            elif LiveUtils.getTrack(track).current_monitoring_state == 1:
                LiveUtils.getTrack(track).current_monitoring_state = 2
            elif LiveUtils.getTrack(track).current_monitoring_state == 2:
                LiveUtils.getTrack(track).current_monitoring_state = 0
        elif len(msg) == 3:
            status = LiveUtils.getTrack(track).current_monitoring_state
            self.oscServer.sendOSC("/monitor", (track, int(status)))
            
    def soloTrackCB(self, msg):
        """Called when a /live/solo message is received.

        Messages:
        /live/solo     (int track)   Solos track number track
        """
        ty = msg[0] == '/live/return/solo' and 1 or 0
        track = msg[2]
        
        if len(msg) == 4:
            if msg[3] == 1:
                status = 0
                if ty == 1:
                    status = LiveUtils.getSong().return_tracks[track].solo
                    if LiveUtils.getSong().exclusive_solo == 1:
                        i = 0
                        for tr in LiveUtils.getSong().return_tracks:
                            LiveUtils.unsoloTrack(i, ty)
                            i = i+1
                else:
                    trk = LiveUtils.getTrack(track)
                    status = trk.solo
                    #trk.color = 12410829
                    if LiveUtils.getSong().exclusive_solo == 1:
                        i = 0
                        for tr in LiveUtils.getTracks():
                            LiveUtils.unsoloTrack(i, ty)
                            
                            i = i+1
                        
                if status == 1:
                    LiveUtils.unsoloTrack(track, ty)
                elif status == 0:
                    LiveUtils.soloTrack(track, ty)
            else:
                LiveUtils.unsoloTrack(track, ty)
            
        elif len(msg) == 3:
            if ty == 1:
                status = LiveUtils.getSong().return_tracks[track].solo
                self.oscServer.sendOSC("/return/solo", (track, int(status)))
                
            else:
                status = LiveUtils.getTrack(track).solo
                self.oscServer.sendOSC("/solo", (track, int(status)))
            
    def volumeCB(self, msg):
        """Called when a /live/volume message is received.

        Messages:
        /live/volume     (int track)                            Returns the current volume of track number track as: /live/volume (int track, float volume(0.0 to 1.0))
        /live/volume     (int track, float volume(0.0 to 1.0))  Sets track number track's volume to volume
        """
        if msg[0] == '/live/return/volume':
            ty = 1
        elif msg[0] == '/live/master/volume':
            ty = 2
        else:
            ty = 0
        
        if len(msg) == 2 and ty == 2:
            self.oscServer.sendOSC("/live/master/volume", LiveUtils.getSong().master_track.mixer_device.volume.value)
        
        elif len(msg) == 3 and ty == 2:
            volume = msg[2]
            LiveUtils.getSong().master_track.mixer_device.volume.value = volume
        
        elif len(msg) == 4:
            track = msg[2]
            volume = msg[3]
            
            if ty == 0:
                LiveUtils.trackVolume(track, volume)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.volume.value = volume

        elif len(msg) == 3:
            track = msg[2]

            if ty == 1:
                self.oscServer.sendOSC("/return/volume", (track, LiveUtils.getSong().return_tracks[track].mixer_device.volume.value))
            
            else:
                self.oscServer.sendOSC("/volume", (track, LiveUtils.trackVolume(track)))
            
    def panCB(self, msg):
        """Called when a /live/pan message is received.

        Messages:
        /live/pan     (int track)                            Returns the pan of track number track as: /live/pan (int track, float pan(-1.0 to 1.0))
        /live/pan     (int track, float pan(-1.0 to 1.0))    Sets track number track's pan to pan

        """
        if msg[0] == '/live/return/pan':
            ty = 1
        elif msg[0] == '/live/master/pan':
            ty = 2
        else:
            ty = 0
        
        if len(msg) == 2 and ty == 2:
            self.oscServer.sendOSC("/live/master/pan", LiveUtils.getSong().master_track.mixer_device.panning.value)
        
        elif len(msg) == 3 and ty == 2:
            pan = msg[2]
            LiveUtils.getSong().master_track.mixer_device.panning.value = pan
            
        elif len(msg) == 4:
            track = msg[2]
            pan = msg[3]
            
            if ty == 0:
                LiveUtils.trackPan(track, pan)
            elif ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.panning.value = pan
            
        elif len(msg) == 3:
            track = msg[2]
            
            if ty == 1:
                self.oscServer.sendOSC("/pan", (track, LiveUtils.getSong().return_tracks[track].mixer_device.panning.value))
            
            else:
                self.oscServer.sendOSC("/pan", (track, LiveUtils.trackPan(track)))

            
    def sendCB(self, msg):
        """Called when a /live/send message is received.

        Messages:
        /live/send     (int track, int send)                              Returns the send level of send (send) on track number track as: /live/send (int track, int send, float level(0.0 to 1.0))
        /live/send     (int track, int send, float level(0.0 to 1.0))     Sets the send (send) of track number (track)'s level to (level)

        """
        ty = msg[0] == '/live/return/send' and 1 or 0
        track = msg[2]
        
        if len(msg) == 5:
            send = msg[3]
            level = msg[4]
            if ty == 1:
                LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value = level
            
            else:
                LiveUtils.trackSend(track, send, level)
        
        elif len(msg) == 4:
            send = msg[3]
            if ty == 1:
                self.oscServer.sendOSC("/live/return/send", (track, send, float(LiveUtils.getSong().return_tracks[track].mixer_device.sends[send].value)))

            else:
                self.oscServer.sendOSC("/live/send", (track, send, float(LiveUtils.trackSend(track, send))))
            
        elif len(msg) == 3:
            if ty == 1:
                sends = LiveUtils.getSong().return_tracks[track].mixer_device.sends
            else:
                sends = LiveUtils.getSong().tracks[track].mixer_device.sends
                
            so = [track]
            for i in range(len(sends)):
                so.append(i)
                so.append(float(sends[i].value))
                
            if ty == 1:
                self.oscServer.sendOSC("/return/send", tuple(so))
            else:
                self.oscServer.sendOSC("/send", tuple(so))
                
        
            
    def pitchCB(self, msg):
        """Called when a /live/pitch message is received.

        Messages:
        /live/pitch     (int track, int clip)                                               Returns the pan of track number track as: /live/pan (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))
        /live/pitch     (int track, int clip, int coarse(-48 to 48), int fine (-50 to 50))  Sets clip number clip in track number track's pitch to coarse / fine

        """
        if len(msg) == 6:
            track = msg[2]
            clip = msg[3]
            coarse = msg[4]
            fine = msg[5]
            LiveUtils.clipPitch(track, clip, coarse, fine)
        if len(msg) ==4:
            track = msg[2]
            clip = msg[3]
            self.oscServer.sendOSC("/pitch", LiveUtils.clipPitch(track, clip))

    def trackJump(self, msg):
        """Called when a /live/track/jump message is received.

        Messages:
        /live/track/jump     (int track, float beats)   Jumps in track's currently running session clip by beats
        """
        if len(msg) == 4:
            track = msg[2]
            beats = msg[3]
            track = LiveUtils.getTrack(track)
            track.jump_in_running_session_clip(beats)

    def trackInfoCB(self, msg):
        """Called when a /live/track/info message is received.

        Messages:
        /live/track/info     (int track)   Returns clip slot status' for all clips in a track in the form /live/track/info (tracknumber, armed  (clipnumber, state, length))
                                           [state: 1 = Has Clip, 2 = Playing, 3 = Triggered]
        """
        
        clipslots = LiveUtils.getClipSlots()
        
        new = []
        if len(msg) == 3:
            new.append(clipslots[msg[2]])
            tracknum = msg[2] - 1
        else:
            new = clipslots
            tracknum = -1
        
        for track in new:
            tracknum = tracknum + 1
            clipnum = -1
            tmptrack = LiveUtils.getTrack(tracknum)
            armed = tmptrack.arm and 1 or 0
            li = [tracknum, armed]
            for clipSlot in track:
                clipnum = clipnum + 1
                li.append(clipnum);
                if clipSlot.clip != None:
                    clip = clipSlot.clip
                    if clip.is_playing == 1:
                        li.append(2)
                        li.append(clip.length)
                        
                    elif clip.is_triggered == 1:
                        li.append(3)
                        li.append(clip.length)
                        
                    else:
                        li.append(1)
                        li.append(clip.length)
                else:
                    li.append(0)
                    li.append(0.0)
                    
            tu = tuple(li)
            
            self.oscServer.sendOSC("/track/info", tu)


    def undoCB(self, msg):
        """Called when a /live/undo message is received.
        
        Messages:
        /live/undo      Requests the song to undo the last action
        """
        LiveUtils.getSong().undo()
        
    def redoCB(self, msg):
        """Called when a /live/redo message is received.
        
        Messages:
        /live/redo      Requests the song to redo the last action
        """
        LiveUtils.getSong().redo()
    
    def releaseClipSlotCB(self, msg):
        if len(msg) == 4:
            track_num = msg[2]
            clip_num = msg[3]
            track = LiveUtils.getTrack(track_num)
            clipslot = track.clip_slots[clip_num]
            try:
                clipslot.set_fire_button_state(False)
            except:
                pass


    def playClipSlotCB(self, msg):
        """Called when a /live/play/clipslot message is received.
        
        Messages:
        /live/play/clipslot     (int track, int clip)   Launches clip number clip in track number track
        """
        if len(msg) == 4:
            track_num = msg[2]
            clip_num = msg[3]
            track = LiveUtils.getTrack(track_num)
            clipslot = track.clip_slots[clip_num]
            try:
                clipslot.set_fire_button_state(True)
            except:
                clipslot.fire()
            
            if clipslot.clip == None:
                if track.arm == 1:
                    self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 4))
                else:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1: 
                            self.oscServer.sendOSC('/clip/playing_status', (track_num, clip_num, 5))
                        else:
                            pass
                    else:
                        pass
    



    def viewSceneCB(self, msg):
        """Called when a /live/scene/view message is received.
        
        Messages:
        /live/scene/view     (int track)      Selects a track to view
        """
        
        if len(msg) == 3:
            scene = msg[2]
            LiveUtils.getSong().view.selected_scene = LiveUtils.getSong().scenes[scene]
            
    def viewTrackCB(self, msg):
        """Called when a /live/track/view message is received.
        
        Messages:
        /live/track/view     (int track)      Selects a track to view
        """
        ty = msg[0] == '/live/return/view' and 1 or 0
        track_num = msg[2]
        
        if len(msg) == 3:
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track_num]
            else:
                track = LiveUtils.getSong().tracks[track_num]
                
            LiveUtils.getSong().view.selected_track = track
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
                
            #track.view.select_instrument()
            
    def mviewTrackCB(self, msg):
        """Called when a /live/master/view message is received.
        
        Messages:
        /live/track/view     (int track)      Selects a track to view
        """
        track = LiveUtils.getSong().master_track

        LiveUtils.getSong().view.selected_track = track
        Live.Application.get_application().view.show_view("Detail/DeviceChain")        
        
        #track.view.select_instrument()
        
    def viewClipCB(self, msg):
        """Called when a /live/clip/view message is received.
        
        Messages:
        /live/clip/view     (int track, int clip)      Selects a track to view
        """
        track = LiveUtils.getSong().tracks[msg[2]]
        scene = LiveUtils.getSong().scenes[msg[3]]

        if len(msg) == 4:
            clip  = msg[3]
        else:
            clip  = 0
        
        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.selected_scene = scene

        LiveUtils.getSong().view.detail_clip = track.clip_slots[clip].clip
        Live.Application.get_application().view.show_view("Detail/Clip")  

    def detailViewCB(self, msg):
        """Called when a /live/detail/view message is received. Used to switch between clip/track detail

        Messages:
        /live/detail/view (int) Selects view where 0=clip detail, 1=track detail
        """
        if len(msg) == 3:
            if msg[2] == 0:
                Live.Application.get_application().view.show_view("Detail/Clip")
            elif msg[2] == 1:
                Live.Application.get_application().view.show_view("Detail/DeviceChain")

    def viewDeviceCB(self, msg):
        """Called when a /live/track/device/view message is received.
        
        Messages:
        /live/track/device/view     (int track)      Selects a track to view
        """
        ty = msg[0] == '/live/return/device/view' and 1 or 0
        track_num = msg[2]
        
        if len(msg) == 4:
            if ty == 1:
                track = LiveUtils.getSong().return_tracks[track_num]
            else:
                track = LiveUtils.getSong().tracks[track_num]

            LiveUtils.getSong().view.selected_track = track
            LiveUtils.getSong().view.select_device(track.devices[msg[3]])
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
            
    def mviewDeviceCB(self, msg):
        track = LiveUtils.getSong().master_track
        
        if len(msg) == 3:
            LiveUtils.getSong().view.selected_track = track
            LiveUtils.getSong().view.select_device(track.devices[msg[2]])
            Live.Application.get_application().view.show_view("Detail/DeviceChain")
        
    def overdubCB(self, msg):
        """Called when a /live/overdub message is received.
        
        Messages:
        /live/overdub     (int on/off)      Enables/disables overdub
        """        
        overdub = msg[2]
        a = LiveUtils.getApp().get_major_version()
        self.oscServer.sendOSC('/overdub_status', int(a))


        if a >= 9:
            self.oscServer.sendOSC('/overdub_status', 1)
            LiveUtils.getSong().arrangement_overdub = overdub
        
        else:
            self.oscServer.sendOSC('/overdub_status', 1)
            LiveUtils.getSong().overdub = overdub
            self.oscServer.sendOSC('/overdub_status', 2)



    def recordCB(self, msg):
        """Called when a /live/record message is received.
        
        Messages:
        /live/record     (int on/off)      Enables/disables recording
        """        
        if len(msg) == 3:
            record = msg[2]
            LiveUtils.getSong().record_mode = record

    def metronomeCB(self, msg):
        """Called when a /live/metronome message is received.
        
        Messages:
        /live/metronome     (int on/off)      Enables/disables metronome
        """        
        if len(msg) == 3:
            metronome = msg[2]
            LiveUtils.getSong().metronome = metronome

    def songpsCB(self, msg):
        
        songtime = LiveUtils.getSong().current_song_time
        self.oscServer.sendOSC("/set/playing_position", (float(songtime) + 0.001))
        
        overdub = LiveUtils.getSong().overdub
        self.oscServer.sendOSC("/set/overdub_status", (int(overdub) + 1))
        
        record = LiveUtils.getSong().record_mode
        self.oscServer.sendOSC("/set/recording_status", (int(record) + 1))
        
        metronome = LiveUtils.getSong().metronome
        self.oscServer.sendOSC("/set/metronome_status", (int(metronome) + 1))
        
        play = LiveUtils.getSong().is_playing
        self.oscServer.sendOSC("/set/playing_status", (int(play) + 1))

        master = LiveUtils.getSong().master_track.mixer_device.volume.value
        self.oscServer.sendOSC("/master/volume", (float(master)))

        returns = LiveUtils.getSong().return_tracks
        for i in range(len(returns)):
            returnv = LiveUtils.getSong().return_tracks[i].mixer_device.volume.value
            self.oscServer.sendOSC("/return/volume", (i, float(returnv)))
            
        

    def stateCB(self, msg):
        """Called when a /live/state is received.
        
        Messages:
        /live/state                    Returns the current tempo and overdub status
        """
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            tempo = LiveUtils.getTempo()
            overdub = LiveUtils.getSong().overdub
            self.oscServer.sendOSC("/state", (tempo, int(overdub)))
        
    def clipInfoCB(self,msg):
        """Called when a /live/clip/info message is received.
        
        Messages:
        /live/clip/info     (int track, int clip)      Gets the status of a single clip in the form  /live/clip/info (tracknumber, clipnumber, state)
                                                       [state: 1 = Has Clip, 2 = Playing, 3 = Triggered]
        """
        
        if len(msg) == 4:
            trackNumber = msg[2]
            clipNumber = msg[3]    
            
            clip = LiveUtils.getClip(trackNumber, clipNumber)
            
            playing = 0
            
            if clip != None:
                playing = 0
                
                if clip.is_playing == 1:
                    playing = 1
                elif clip.is_triggered == 1:
                    playing = 2

            self.oscServer.sendOSC("/clip/playing_status", (trackNumber, clipNumber, playing))
        
        return
        
    def deviceCB(self, msg):
        fxview = msg[2]
        track = msg[3]
        device = msg[4]
        po = [fxview]
        po.append(int(track))
        po.append(int(device))
        if len(msg) == 5: 
            params = LiveUtils.getSong().tracks[track].devices[device].parameters
            name = LiveUtils.getSong().tracks[track].name
            devicename = LiveUtils.getSong().tracks[track].devices[device].name
            po.append(repr2(name))
            po.append(repr2(devicename))
            
            is_selected = 0
        
            if device == LiveUtils.getSong().appointed_device:
                is_selected = 1
        
            po.append(int(is_selected))
            
            for i in range(len(params)):
                po.append(float(params[i].value))
                po.append(repr2(params[i].name))
                po.append(repr2(params[i].__str__()))
            self.oscServer.sendOSC("/track/device/parameters", tuple(po))                          
    
        elif len(msg) == 6:
            track = msg[2]
            device = msg[3]
            param  = msg[4]
            value  = msg[5]
            LiveUtils.getSong().tracks[track].devices[device].parameters[param].value = value

    def returndeviceCB(self, msg):
        fxview = msg[2]
        track = msg[3]
        device = msg[4]
        po = [fxview]
        po.append(int(track))
        po.append(int(device))
        
        if len(msg) == 5: 
            params = LiveUtils.getSong().return_tracks[track].devices[device].parameters
            name = LiveUtils.getSong().return_tracks[track].name
            devicename = LiveUtils.getSong().return_tracks[track].devices[device].name
            po.append(repr2(name))
            po.append(repr2(devicename))

            for i in range(len(params)):
                po.append(float(params[i].value))
                po.append(repr2(params[i].name))
                po.append(repr2(params[i].__str__()))
            self.oscServer.sendOSC("/return/device/parameters", tuple(po))

        elif len(msg) == 6:
            track = msg[2]
            device = msg[3]
            param  = msg[4]
            value  = msg[5]
            LiveUtils.getSong().return_tracks[track].devices[device].parameters[param].value = value

        


    def parameterblockCB(self, msg):
        track = msg[2]
        device = msg[3]
        po = []
        po.append(track)
        po.append(device)
        params = LiveUtils.getSong().tracks[track].devices[device].parameters
                
        for i in range(len(params)):
            po.append(params[i].min)
            po.append(params[i].max)
            po.append(params[i].value)
            po.append(repr2(params[i].name))
            po.append(params[i].is_quantized+1)
                
        self.oscServer.sendOSC("/parameterblock", tuple(po))

    def returnparameterblockCB(self, msg):
        track = msg[2]
        device = msg[3]
        po = []
        po.append(track)
        po.append(device)
        params = LiveUtils.getSong().return_tracks[track].devices[device].parameters
                
        for i in range(len(params)):
            po.append(params[i].min)
            po.append(params[i].max)
            po.append(params[i].value)
            po.append(repr2(params[i].name))
            po.append(params[i].is_quantized+1)
                
        self.oscServer.sendOSC("/return/parameterblock", tuple(po))

    def masterparameterblockCB(self, msg):
        device = msg[2]
        po = []
        po.append(0)
        po.append(device)
        params = LiveUtils.getSong().master_track.devices[device].parameters
                
        for i in range(len(params)):
            po.append(params[i].min)
            po.append(params[i].max)
            po.append(params[i].value)
            po.append(repr2(params[i].name))
            po.append(params[i].is_quantized+1)
                
        self.oscServer.sendOSC("/master/parameterblock", tuple(po))



                
    def deviceSelect(self, msg):
        fxview = msg[2]
        track = msg[3]
        device = msg[4]
        params = 0
        if track == 1000:
            params = LiveUtils.getSong().master_track.devices[device].parameters
        elif track >= 2000:
            params = LiveUtils.getSong().return_tracks[int(track/1000)-2].devices[device].parameters

        else:
            params = LiveUtils.getSong().tracks[track].devices[device].parameters
            
        block = [fxview]                           
        if len(params) == 10:
            block.extend([1])
        elif len(params) == 9:
            block.extend([1])
        else:
            block.extend([0])

        self.oscServer.sendOSC("/devicerack", block)

    def devCB(self, msg):
        #time.sleep(0.1)
        trackNr = 0
        onoff = 0
        for track in LiveUtils.getTracks():
            devices = LiveUtils.getSong().tracks[trackNr].devices
            num = len(devices)
            for i in range(len(devices)):
                nm = repr2(devices[i].name)
                device = LiveUtils.getSong().tracks[trackNr].devices[i]
                params = device.parameters
                numParam = len(params)
                onoff = params[0].value
                cnam = repr2(device.class_name)
                self.oscServer.sendOSC("/track/device", (0, trackNr, i, nm, onoff, num, numParam, cnam))
                 #wait 0.01 seconds
            trackNr = trackNr +1

    def rdevCB(self, msg):
        #time.sleep(0.05)
        trackNr = 0
        tracks = LiveUtils.getSong().return_tracks
        for track in tracks:
            devices = LiveUtils.getSong().return_tracks[trackNr].devices
            num = len(devices)
            for i in range(len(devices)):
                nm = repr2(devices[i].name)
                device = LiveUtils.getSong().return_tracks[trackNr].devices[i]
                params = device.parameters
                numParam = len(params)
                onoff = params[0].value
                cnam = repr2(device.class_name)
                self.oscServer.sendOSC("/return/device", (2, trackNr, i, nm, onoff, num, numParam, cnam))
                 #wait 0.01 seconds
            trackNr = trackNr +1

    def mdevCB(self, msg):
        #time.sleep(0.05)
        devices = LiveUtils.getSong().master_track.devices
        num = len(devices)
        for i in range(len(devices)):
            nm = repr2(devices[i].name)
            device = LiveUtils.getSong().master_track.devices[i]
            params = device.parameters
            numParam = len(params)
            onoff = params[0].value
            cnam = repr2(device.class_name)
            self.oscServer.sendOSC("/master/device", (1, i, nm, onoff, num, numParam, cnam))
             #wait 0.01 seconds
                

    def trackdeviceblockCB(self, msg):

        track = msg[2]
        block = []
        block.extend([track])
        devices = LiveUtils.getSong().tracks[track].devices
        for i in range(len(devices)):
            block.extend([repr2(devices[i].name)])
        self.oscServer.sendOSC("/deviceblock", block)

    def returndeviceblockCB(self, msg):

        track = msg[2]
        block = []
        block.extend([track])
        devices = LiveUtils.getSong().return_tracks[track].devices
        for i in range(len(devices)):
            block.extend([repr2(devices[i].name)])
        self.oscServer.sendOSC("/returndeviceblock", block)



        
    def masterdeviceblockCB(self, msg):

        block = []
        devices = LiveUtils.getSong().master_track.devices
        for i in range(len(devices)):
            block.extend([repr2(devices[i].name)])
        for a in range (23-(len(devices))):
            block.extend(["0"])
        self.oscServer.sendOSC("/masterdeviceblock", block)

    def deviceBlockCB(self, msg): 
        """Called when a /live/deviceblock message is received.

        /live/deviceblock    (int offset, int blocksize) Returns a list of blocksize track names starting at offset
        """
        if len(msg) == 4:
            trackOffset = msg[2]
            blocksize = msg[3]
            size = 8
            for track in range(0, blocksize):
                block = []
                block.extend([track])
                block.extend([trackOffset])
                devices = LiveUtils.getSong().tracks[track+trackOffset].devices
                for i in range(len(devices)):
                    block.extend([repr2(LiveUtils.getSong().tracks[track+trackOffset].devices[i].name)])    

                self.oscServer.sendOSC("/bigdeviceblock", block)
           

    def mdeviceCB(self, msg):
        if len(msg) == 4:
            fxview = msg[2]
            device = msg[3]
            po = [fxview]
            po.append(0)
            po.append(int(device))
            name = LiveUtils.getSong().master_track.name
            devicename = LiveUtils.getSong().master_track.devices[device].name
            po.append(repr2(name))
            po.append(repr2(devicename))

            params = LiveUtils.getSong().master_track.devices[device].parameters
    
            for i in range(len(params)):
                po.append(float(params[i].value))
                po.append(repr2(params[i].name))
                po.append(repr2(params[i].__str__()))
            
            self.oscServer.sendOSC("/master/device/parameters", tuple(po))
    
        elif len(msg) == 4:
            device = msg[2]
            param  = msg[3]
            
            p = LiveUtils.getSong().master_track.devices[device].parameters[param]
        
            self.oscServer.sendOSC("/master/device", (device, param, p.value, repr2(p.name)))
    
        elif len(msg) == 5:
            device = msg[2]
            param  = msg[3]
            value  = msg[4]
        
            LiveUtils.getSong().master_track.devices[device].parameters[param].value = value


    
            
    def mdevicelistCB(self, msg):
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            #time.sleep(0.05)
            do = []
            devices = LiveUtils.getSong().master_track.devices
        
            for i in range(len(devices)):
                do.append(i)
                do.append(repr2(devices[i].name))
            
            self.oscServer.sendOSC("/master/devicelist", tuple(do))

            
            
            
    def crossfaderCB(self, msg):
        if len(msg) == 2 or (len(msg) == 3 and msg[2] == "query"):
            self.oscServer.sendOSC("/master/crossfader", float(LiveUtils.getSong().master_track.mixer_device.crossfader.value))
        
        elif len(msg) == 3:
            val = msg[2]
            LiveUtils.getSong().master_track.mixer_device.crossfader.value = val



    def loopStateCB(self, msg):
        type = msg[0] == '/clip/loopstate_id' and 1 or 0
    
        trackNumber = msg[2]
        clipNumber = msg[3]
    
        if len(msg) == 4:
            if type == 1:
                self.oscServer.sendOSC("/clip/loopstate", (trackNumber, clipNumber, int(LiveUtils.getClip(trackNumber, clipNumber).looping)))
            else:
                self.oscServer.sendOSC("/clip/loopstate", (int(LiveUtils.getClip(trackNumber, clipNumber).looping)))    
        
        elif len(msg) == 5:
            loopState = msg[4]
            LiveUtils.getClip(trackNumber, clipNumber).looping =  loopState



    def quantizationCB(self, msg):
        quant = msg[2]
        LiveUtils.getSong().clip_trigger_quantization = quant

    def recquantizationCB(self, msg):
        recquant = msg[2]
        LiveUtils.getSong().midi_recording_quantization = recquant

    def quantsCB(self, msg):
        self.oscServer.sendOSC("/set/quantization", (int(LiveUtils.getSong().clip_trigger_quantization), int(LiveUtils.getSong().midi_recording_quantization)))




    def send_values_for_device(self, device, track, tid, did, type, number_of_steps, indices):
        
        
        nm = repr2(device.name)
        params = device.parameters
        onoff = params[0].value
        num = len(track.devices)
        numParams = len(params)
        cnam = repr2(device.class_name)
        
        
        tr = tid
        dev = did
        
        name = track.name
        devicename = device.name
        
        po = [type]
        po.append(int(tr))
        po.append(int(dev))
        
        
        is_selected = 0
        
        if device == LiveUtils.getSong().appointed_device:
            is_selected = 1
        
        
        po2 = [type]
        po2.append(int(tr))
        po2.append(int(dev))
        po2.append(repr2(name))
        po2.append(repr2(devicename))
        
        po2.append(int(is_selected))
        
        po.append(int(number_of_steps))
        po2.append(int(number_of_steps))
        
        for index in range(number_of_steps * 2):
            po.append(int(indices[index]))
            po2.append(int(indices[index]))
        

        for j in range(len(params)):
            po.append(params[j].min)
            po.append(params[j].max)
            po.append(params[j].is_quantized+1)
            po2.append(float(params[j].value))
            po2.append(repr2(params[j].name))
            po2.append(repr2(params[j].__str__()))


        self.oscServer.sendOSC("/device/range", tuple(po))
        self.oscServer.sendOSC("/master/device/parameters", tuple(po2))



    def send_update_for_device(self, device, track, tid, did, type, num, number_of_steps, indices, i):

        
        if i != -1:
            indices.append(int(i))
            number_of_steps = number_of_steps+1
        
        
        nm = repr2(device.name)
        params = device.parameters
        onoff = params[0].value
        numParams = len(params)
        cnam = repr2(device.class_name)


        tr = tid
        dev = did
        
        name = track.name
        devicename = device.name
        
        
        is_selected = 0
        
        if device == LiveUtils.getSong().appointed_device:
            is_selected = 1
        
        po = [type]
        po.append(int(tr))
        po.append(int(dev))
        
        
        po2 = [type]
        po2.append(int(tr))
        po2.append(int(dev))
        po2.append(repr2(name))
        po2.append(repr2(devicename))
        po2.append(int(is_selected))
        
        po.append(int(number_of_steps))
        po2.append(int(number_of_steps))
        

        for index in range(number_of_steps * 2):
            po.append(int(indices[index]))
            po2.append(int(indices[index]))
        
        
        for j in range(len(params)):
            po.append(params[j].min)
            po.append(params[j].max)
            po.append(params[j].is_quantized+1)
            po2.append(float(params[j].value))
            po2.append(repr2(params[j].name))
            po2.append(repr2(params[j].__str__()))
            
            
        try:
            can_have_chains = device.can_have_chains
        except:
            can_have_chains = 0
        try:
            can_have_drumpads = device.can_have_drum_pads and device.has_drum_pads and device.class_name == 'MultiSampler' or device.class_name == "DrumGroupDevice"
        except:
            can_have_drumpads = 0

        if type == 0:
            
            
            
            
            po3 = [type, tid, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            self.oscServer.sendOSC('/track/device', (tuple(po3)))
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/track/device/parameters", tuple(po2))
            #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPADS"), int(1)))

            if can_have_drumpads:
                drum_pads_tuple = [type, tid, did, number_of_steps]
                for index in range(number_of_steps * 2):
                    drum_pads_tuple.append(int(indices[index]))
                
                for drum_pad in device.drum_pads:

                    drum_pads_tuple.append(int(drum_pad.note))
                    drum_pads_tuple.append(repr2(drum_pad.name))
                    drum_pads_tuple.append(int(drum_pad.mute))
                    drum_pads_tuple.append(int(drum_pad.solo))
                    #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPAD"), repr2(drum_pad.name)))

                self.oscServer.sendOSC("/track/device/drumpads", tuple(drum_pads_tuple))
            #self.oscServer.sendOSC("/NSLOG_REPLACE", (str("SENDING DRUMPADS"), int(34)))

        
        elif type == 2:
            
            po3 = [type, tid, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            self.oscServer.sendOSC('/return/device', (tuple(po3)))
            
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/return/device/parameters", tuple(po2))

        
        elif type == 1:
            po3 = [type, 0, did, nm, onoff, int(num), numParams, int(can_have_drumpads), cnam, int(can_have_chains), number_of_steps]
            for index in range(number_of_steps * 2):
                po3.append(int(indices[index]))
            
            self.oscServer.sendOSC('/master/device', (tuple(po3)))
            
            self.oscServer.sendOSC("/device/range", tuple(po))
            self.oscServer.sendOSC("/master/device/parameters", tuple(po2))
        

        if can_have_chains == 1:
            
            for chain_id in range(len(device.chains)):
                chain = device.chains[chain_id]
                
                
                indis = list(indices)
                indis.append(int(chain_id))
                
                po3 = [type, tid, did, repr2(chain.name), number_of_steps]
                for index in range(number_of_steps * 2 + 1):
                    po3.append(int(indis[index]))
                
                self.oscServer.sendOSC('/device_chain', (tuple(po3)))
                
                
                for device_id in range(len(chain.devices)):
                    dev = chain.devices[device_id]
                    
                    lis = list(indis)
                    self.send_update_for_device(dev, track, tid, did, type, len(chain.devices), number_of_steps, lis, device_id)





    def load_devices_for_track(self, track, tid, type):
        if len(track.devices) == 0:
            self.oscServer.sendOSC('/devices_empty', (int(type), int(tid)))
        
        did = 0
        
        number_of_steps = 0
        i = 0
        indices = []
        
        for device in track.devices:
            
            lis = list(indices)
            
            self.send_update_for_device(device, track, tid, did, type, len(track.devices), number_of_steps, lis, -1)
            did = did+1

        self.oscServer.sendOSC('/devices_loaded', (int(type), int(tid)))



    def load_device_values(self, msg):
        
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

        indices = []

        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]

            chain = device.chains[chain_id]
            indices.append(int(chain_id))

            device = chain.devices[device_id]
            indices.append(int(device_id))


        self.send_values_for_device(device, track, tid, did, type, number_of_steps, indices)


    def change_device_parameter(self, msg):
        
        type = msg[2]
        tid = msg[3]
        did = msg[4]
        pid = msg[5]
        value = msg[6]
        
        number_of_steps = msg[7]

        if type == 0:
            track = LiveUtils.getSong().tracks[tid]
        
        elif type == 2:
            track = LiveUtils.getSong().return_tracks[tid]
        elif type == 1:
            track = LiveUtils.getSong().master_track
        
        device = track.devices[did]
        indices = []

        for i in range(number_of_steps):
            chain_id = msg[8+i*2]
            device_id = msg[9+i*2]
            
            chain = device.chains[chain_id]
            indices.append(int(chain_id))
            
            device = chain.devices[device_id]
            indices.append(int(device_id))


        device.parameters[pid].value = float(value)


    def focusDevice(self, msg):

        type = msg[2]
        track_id = msg[3]
        device_id = msg[4]
        number_of_steps = msg[5]


        if type == 1:

            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:

            track = LiveUtils.getSong().return_tracks[track_id]
        else:

            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]

        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]


        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.select_device(device)
        Live.Application.get_application().view.show_view("Detail/DeviceChain")


    def focusChain(self, msg):
        self.oscServer.sendOSC('/focus_chain', 1)
        
        type = msg[2]
        track_id = int(msg[3])
        device_id = int(msg[4])
        number_of_steps = msg[5]
        
        
        if type == 1:
            self.oscServer.sendOSC('/focus_normal_track', ((track_id)))
            
            track = LiveUtils.getSong().tracks[track_id]
        elif type == 3:
            self.oscServer.sendOSC('/focus_return_track', ((track_id)))
            
            track = LiveUtils.getSong().return_tracks[track_id]
        else:
            self.oscServer.sendOSC('/focus_master_track', (int(type)))
            
            track = LiveUtils.getSong().master_track
        
        device = track.devices[device_id]
        
        for i in range(number_of_steps):
            chain_id = msg[6+i*2]
            device_id = msg[7+i*2]
            
            chain = device.chains[chain_id]
            device = chain.devices[device_id]
        
        self.oscServer.sendOSC('/focus_chain', 2)

        chain_id = msg[6+number_of_steps*2]
        
        chain = device.chains[chain_id]
        self.oscServer.sendOSC('/focus_chain', chain_id)

        Live.Application.get_application().view.show_view("Detail/DeviceChain")
        LiveUtils.getSong().view.selected_track = track
        LiveUtils.getSong().view.select_device(device)
        browser = Live.Application.get_application().browser
        device.view.selected_chain = chain

        browser.hotswap_target = chain
        

        self.oscServer.sendOSC('/focus_chain', 4)





