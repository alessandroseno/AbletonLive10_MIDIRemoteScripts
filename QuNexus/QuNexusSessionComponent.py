from _Framework.SessionComponent import SessionComponent


class QuNexusSessionComponent(SessionComponent):
  """ Custom session component for QuNexus that automatically selects first track in red box """

  #def __init__(self, num_tracks = 0, num_scenes = 0, *a, **k)
    #SessionComponent.__init__(self, num_tracks, num_scenes, *a, **k)
  
  def update(self):
    SessionComponent.update(self)
    self._reselect_track()

  """ Because update doesn't get called in Live 9 when we change offsets 
      We have to manually call reselect_track whenever we bank
  """
  def set_offsets(self, track_offset, scene_offset):
    SessionComponent.set_offsets(self, track_offset, scene_offset)
    self._reselect_track()

  def _reselect_track(self):
    tracks_to_use = self.tracks_to_use()
    track = tracks_to_use[self._track_offset] 
    self.song().view.selected_track = track 




