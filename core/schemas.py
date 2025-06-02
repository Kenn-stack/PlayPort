from ninja import Schema
from typing import List

class Track(Schema):
  href: str
  total: int
  
class Image(Schema):
  url: str

class Item(Schema):
  id: str
  name: str
  images: List[Image]
  tracks: Track
  
class ExtractedPlaylist(Schema):
  items: List[Item]
  
  
class Artists(Schema):
  name: str
  
class PlayListTrack(Schema):
  name: str
  artists: List[Artists]
  
  
class PlayListItem(Schema): 
  track: PlayListTrack
  
  
class TrackItems(Schema):
  items: List[PlayListItem]
  
'''class ExtractedPlaylistDetail(Schema):
  name: str
  tracks: TrackItems'''