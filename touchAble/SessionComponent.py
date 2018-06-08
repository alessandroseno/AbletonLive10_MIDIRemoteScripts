# (c) 2014 Sigabort, Lee Huddleston, Isotonik Studios; admin@sigabort.co, http://sigabort.co, http://www.isotonikstudios.com

import Live

from _Framework.SessionComponent import SessionComponent as SessionComponentBase
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, subject_slot_group

class TouchableSessionComponent(SessionComponentBase):
	def __init__(self, touchAble, num_tracks = 0, num_scenes = 0, *a, **k):
		SessionComponentBase.__init__(self, num_tracks, num_scenes, *a, **k)

		self.touchAble = touchAble
		self._logging = True
		
		self._lsync_relation = -1
		self._lsync_track_offset = 0
		self._lsync_scene_offset = 0
		self._lsync_w = 8;
		self._lsync_h = 8;
		self._touchable_x = -1;
		self._touchable_y = -1;
		self._touchable_w = -1;
		self._touchable_h = -1;
		
		self._touchable_update_count = 0;
		self._process_broadcast = True
		
		self._setup_controls()

	def _log( self, msg, force = False ):
		if self._logging or force:
			self.touchAble.log_message( msg )
		
	def _ping(self, msg):
		self._touchable_update_count = self._touchable_update_count - 1
		
		if self._touchable_update_count < 0:
			self._touchable_update_count = 15
			self._send_lsync_coords( "7" )
						
	def _set_lsync_offsets_from_touchable( self, track_offset, scene_offset, w, h, force = False ):
		self._set_lsync_offsets( track_offset, scene_offset, w, h, force )
		
	def _set_lsync_offsets( self, track_offset, scene_offset, w, h, force = False ):
		self._log( "session: set_offsets: " + str( track_offset ) + ", " + str( scene_offset ) + ", w: " + str( w ) + ", h: " + str( h ) +", curr: " + str( self._track_offset.value ) + ", " + str( self._scene_offset.value ) )

		touchable_changed = False
		
		if self._touchable_w != w:
			self._touchable_w = w
			touchable_changed = True
			
		if self._touchable_h != h:
			self._touchable_h = h
			touchable_changed = True

#		adjusted_track_offset = track_offset 
#		adjusted_scene_offset = scene_offset 
		
		# can't remember why this was commented, but without it, coords sent back to m4l aren't updated for relation
		adjusted_track_offset = track_offset + self._lsync_track_offset;
		adjusted_scene_offset = scene_offset + self._lsync_scene_offset;
		
		update_highlight = False
		
		if track_offset != -1 and scene_offset != -1:
			if hasattr( self, '_track_offset' ) and ( self._track_offset.value != track_offset or force ):
				self._log( "Sending track offset: " + str( adjusted_track_offset ) )
				self._track_offset.receive_value( adjusted_track_offset )
				self._track_offset.value = track_offset
				update_highlight = True
						
			if hasattr( self, '_scene_offset' ) and ( self._scene_offset.value != scene_offset or force ):
				self._log( "Sending scene offset: " + str( adjusted_scene_offset ) )
				self._scene_offset.receive_value( adjusted_scene_offset )
				self._scene_offset.value = scene_offset
				update_highlight = True

			if hasattr( self, '_session_width' ) and ( self._session_width.value != w or force ):
				self._log( "Sending session width: " + str( self._session_width ) )
				self._session_width.receive_value( w )
				self._session_width.value = w

			if hasattr( self, '_session_height' ) and ( self._session_height.value != w or force ):
				self._log( "Sending session height: " + str( self._session_height ) )
				self._session_height.receive_value( h )
				self._session_height.value = h

#		if touchable_changed:
#			self._send_lsync_coords();

		if update_highlight:
			self.set_highlight( track_offset, scene_offset, w, h )
			
#	@subject_slot_group('playing_slot_index')
#	def _on_playing_slot_index_changed(self, track_index):
#		self.touchAble.log_message( "index: " + str( track_index ) )
#		pass
			
	def _reassign_tracks(self):
		pass
	
	def _reassign_scenes(self):
		pass
	
	def _change_offsets(self, track_increment, scene_increment):
		pass

	def set_offsets(self, track_offset, scene_offset):
		pass
    	
	def set_highlight( self, x, y, w = -1, h = -1 ):
		self._log( "set highlight: " + str( x ) + ", " + str( y ) + ", " + str( w ) + ", " + str( h ) )	

		if x < 0:
			x = 0
			
		if y < 0:
			y = 0
			
		if w == -1:
			w = self._touchable_w
			
		if h == -1:
			h = self._touchable_h
			
		self.touchAble._set_session_highlight( x, y, w, h, False )
					
	def set_launchsync_relation( self, val ):
		self._log( "set_launchsyc_relation: " + str( val ) )

		self._lsync_relation = val
		self._lsync_track_offset = self._touchable_x
		self._lsync_scene_offset = self._touchable_y
		
		if val == 1:
			self._lsync_track_offset = self._touchable_x + self._touchable_w
		elif val == 2:
			self._lsync_scene_offset = self._touchable_y + self._touchable_h
		elif val == 3:
			self._lsync_track_offset = self._touchable_x - self._lsync_w
			
			if self._lsync_track_offset < 0:
				self._lsync_track_offset = 0
		elif val == 4:
			self._lsync_scene_offset = self._touchable_y - self._lsync_h
			
			if self._lsync_scene_offset < 0:
				self._lsync_scene_offset = 0
			
		self._set_lsync_offsets( 0, 0, self._touchable_w, self._touchable_h, True )
		self._send_lsync_coords( "3" );
					
	def set_launchsync_position( self, track_offset, scene_offset ):
		self._log( "set_launchsyc_position: " + str( track_offset ) + ", " + str( scene_offset ) )
		self._lsync_track_offset = track_offset
		self._lsync_scene_offset = scene_offset
		self._send_lsync_coords( "4" )

	def set_session_offsets( self, track_offset, scene_offset ):
		self._log( "set_session_offsets: " + str( track_offset ) + ", " + str( scene_offset ) )
#		self.touchAble.set_offsets( track_offset, scene_offset )

#		self._track_offset.value = track_offset			
#		self._scene_offset.value = scene_offset

#		self.set_highlight( track_offset, scene_offset )

		self._send_lsync_coords( "5", True, track_offset, scene_offset )
	
	def _broadcast( self, msg ):
#		self._log( "_broadcast: " + str( self._process_broadcast ) + ", " + str( self._touchable_update_count ) )

		op = msg[2]
		type = msg[3]
		name = msg[4]
		w = msg[5]
		h = msg[6]
		pos_x = msg[7]
		pos_y = msg[8]
		track_offset = msg[9]
		scene_offset = msg[10]
		touchable_changed = False
		
		if self._touchable_x != pos_x:
			self._touchable_x = pos_x
			touchable_changed = True
			
		if self._touchable_y != pos_y:
			self._touchable_y = pos_y
			touchable_changed = True
			
		if self._touchable_w != w:
			self._touchable_w = w
			touchable_changed = True
			
		if self._touchable_h != h:
			self._touchable_h = h
			touchable_changed = True
			
#		self._touchable_update_count = self._touchable_update_count - 1

		self._log( "broadcast: op: " + str( op ) + ", w: " + str( w ) + ", h: " + str( h ) + ", pos_x: " + str( pos_x ) + ", pos_y: " + str( pos_y ) + ", track_offs: " + str( track_offset ) + ", scene_offs: " + str( scene_offset ) + ", process: " + str( self._process_broadcast ) + ", changed: " + str( touchable_changed ) )

#		self._set_lsync_offsets( int( round( track_offset ) ), int( round( scene_offset ) ), w, h )
		
		if self._process_broadcast == False and touchable_changed == False:
			return
			
#		if touchable_changed:
#			self.set_launchsync_relation( self._lsync_relation )
		
		if self._process_broadcast:
			self.set_highlight( 0, 0, w, h )
			self._send_lsync_coords( "2" );
		
		self._process_broadcast = False
				
	def _send_lsync_coords( self, id, force = False, track_offset = -1, scene_offset = -1 ):  
		if self._lsync_relation != -1 or force:
			x_offset = self._lsync_track_offset + ( self._track_offset.value if track_offset == -1 else track_offset )
			y_offset = self._lsync_scene_offset + ( self._scene_offset.value if scene_offset == -1 else scene_offset )
			
#			if self._lsync_relation == 1:
#				x_offset = self._lsync_track_offset + self._track_offset.value - self._touchable_x
#			elif self._lsync_relation == 2:
#				y_offset = self._lsync_scene_offset + self._scene_offset.value - self._touchable_y
#			elif self._lsync_relation == 3:
#				pass
#			elif self._lsync_relation == 4:
#				pass
			
#			x_offset = self._lsync_track_offset + self._track_offset.value - self._touchable_x
#			y_offset = self._lsync_scene_offset + self._scene_offset.value - self._touchable_y
			
			self._log( "session: _send_lsync_coords: " + str( id ) + ", lsync_offs: " + str( self._lsync_track_offset ) + ", " + str( self._lsync_scene_offset ) + ", session_offs: " + str( self._track_offset.value ) + ", " + str( self._scene_offset.value ) + ", final: " + str( x_offset ) + ", " + str( y_offset ) )
			
			msg = ( int( 1 ), 'Launchsync', 'Launchsync', int( self._lsync_w ), int( self._lsync_h ), int( self._lsync_track_offset ), int( self._lsync_scene_offset  ), float( x_offset ), float( y_offset ) )
			
			self.touchAble.oscServer.sendOSC( "/broadcast", msg )
			self._log( "/broadcast: " + str( msg ) )
			
	def _setup_controls( self ):  
		self._log( "_setup_controls", True )
		self._track_offset = EncoderElement( MIDI_CC_TYPE, 15, 118, Live.MidiMap.MapMode.absolute )
		self._track_offset.value = 0
		self._track_offset.name = "Track_Offset" 
		self._scene_offset = EncoderElement( MIDI_CC_TYPE, 15, 119, Live.MidiMap.MapMode.absolute ) 
		self._scene_offset.value = 0
		self._scene_offset.name = "Scene_Offset" 
		self._session_width = EncoderElement( MIDI_CC_TYPE, 15, 120, Live.MidiMap.MapMode.absolute )
		self._session_width.value = 0
		self._session_width.name = "Session_Height" 
		self._session_height = EncoderElement( MIDI_CC_TYPE, 15, 121, Live.MidiMap.MapMode.absolute ) 
		self._session_height.value = 0
		self._session_height.name = "Session_Width" 
		self.touchAble.request_rebuild_midi_map()
		self._log( "_setup_controls complete", True )
    
