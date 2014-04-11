PLUGIN_NAME = 'MusicBee Compatibility'
PLUGIN_AUTHOR = 'Volker Zell (and Sophist)'
PLUGIN_DESCRIPTION = '''
Provide MusicBee compatible tags.
<br/><br/>
Note 1: The tags used by this plugin are only populated when you have checked Options / Metadata / Use track relationships.
<br/>
Note 2: Info copied includes ALL Performers, as well as the Composer, Producer, Mixer etc.
<br/>
<pre>
MusicBee:               MusicBrainz tag:    MusicBrainz source:
Display Artist          DISPLAY ARTIST      artist
Artists:Artist          artist              artists (or split of artist if not existing)
Artists:Guest           GUEST ARTIST        taken from artist or title tags after feat./featuring/(feat./(featuring
Artists:Performer       PERFORMER           performer:*
Musician Credits List   TMCL                performer:*
Involved People List    IPLS                'Arranger', 'Engineer', 'Producer', 'Mixer', 'DJMixer', 'Remixer', 'Conductor'
Comment                 comment:            All the above
Misc                    MISC                'CatalogNumber', 'Barcode', 'ASIN', 'ReleaseType', 'ReleaseStatus', 'ReleaseCountry'
</pre>
Note 3: I use the following additional entry in CustomTagConfig.xml for MusicBee
<pre>
  &lsaquo;Tag id="Misc" id3v23="TXXX/MISC" id3v24="TXXX/MISC" wma="Misc" vorbisComments="Misc" mpeg="Misc" ape2="Misc" /&rsaquo;
</pre>
and a couple of Virtual Columns with the following structure (because I ran out of the 16 custom columns) to access the MISC entries:
<pre>
  Catalognumber = $Replace($First($Split(&lsaquo;Misc&rsaquo;,Catalognumber:,2)),",",;)
</pre>
'''
PLUGIN_VERSION = "0.5"
PLUGIN_API_VERSIONS = ["0.15.0", "0.15.1", "0.16.0", "1.0.0", "1.1.0", "1.2.0", "1.3.0"]

import re
from picard import log
from picard.metadata import register_track_metadata_processor

class MusicBeeCompatibility:

    re_artist_split = re.compile(r",\s*|\s+&\s+|\s+and\s+|\s+feat[.:]\s+|\s+featuring\s+").split
    re_featured_split = re.compile(r"\s+\(?feat[.:]\s+|\s+featuring\s+").split

    def musicbee_compatibility(self, album, metadata, *args):
        self.re_artist_split = MusicBeeCompatibility.re_artist_split
        self.re_featured_split = MusicBeeCompatibility.re_featured_split
        self.populate_performers(metadata)
        self.populate_artist(metadata)
        self.populate_writer(metadata)
        self.populate_tipl(metadata)
        self.populate_misc(metadata)
        self.populate_comment(metadata)

    def populate_performers(self, metadata):
        performers = []
        for name in [name for name in metadata if name.startswith('performer:')]:
            self.txxx_add(metadata, 'TMCL', name[10:].title(), name, '; ')
            performers += dict.get(metadata, name)
        metadata["PERFORMER"] = "\x00".join(set(performers))

    def populate_artist(self, metadata):
        if 'artists' in metadata:
            artists = dict.get(metadata, "artists")
        elif 'artist' in metadata:
            artists = self.re_artist_split(metadata['artist'])
        else:
            return

        guests = []
        if 'artist' in metadata:
            guest = self.re_featured_split(metadata['artist'], 1)[1:]
            if guest:
                guests += self.re_artist_split(guest[0].rstrip(')'))
        if 'title' in metadata:
            guest = self.re_featured_split(metadata['title'], 1)[1:]
            if guest:
                guests += self.re_artist_split(guest[0].rstrip(')'))

        artists = [x for x in artists if x not in guests]

        metadata["DISPLAY ARTIST"] = metadata["artist"]
        metadata["artist"] = "\x00".join(artists)
        metadata["GUEST ARTIST"] = "\x00".join(guests)

    def populate_writer(self, metadata):
        if not "writer" in metadata:
            return
        self.metadata_merge(metadata, 'composer', 'writer')
        self.metadata_merge(metadata, 'lyricist', 'writer')
        del metadata["writer"]

    def metadata_merge(self, metadata, old, new):
        oldvals = dict.get(metadata, old, [])
        newvals = dict.get(metadata, new, [])
        metadata[old] = list(set(oldvals + newvals))

    def populate_tipl(self, metadata):
        for name in ['Arranger', 'Engineer', 'Producer', 'Mixer', 'DJMixer']:
          if name.lower() in metadata:
            metadata[name] = "\x00".join(dict.get(metadata, name.lower()))

        for name in ['Arranger', 'Engineer', 'Producer', 'Mixer', 'DJMixer', 'Remixer', 'Conductor']:
             self.txxx_add(metadata, 'IPLS', name, name, '; ')

    def populate_misc(self, metadata):
        for name in ['CatalogNumber', 'Barcode', 'ASIN', 'ReleaseType', 'ReleaseStatus', 'ReleaseCountry']:
             self.txxx_add(metadata, 'MISC', name, name, '; ')

    def populate_comment(self, metadata):
        for name in ['Composer', 'Lyricist', 'Conductor', 'Arranger', 'Engineer', 'Producer', 'Mixer', 'Remixer', 'DJMixer']:
             self.txxx_add(metadata, 'comment:', _(name), name.lower(), '\n')
        for name in metadata.keys():
            if name.startswith('performer:'):
                self.txxx_add(metadata, 'comment:', name[10:].title(), name, '\n')

    def txxx_add(self, metadata, tagname, label, name, joiner):
        name = name.lower()
        if not name in metadata:
            return
        tag = dict.get(metadata, name)
        value = ', '.join(tag)
        if label:
            label += ': '
        if tagname in metadata:
            metadata[tagname] += joiner + label + value
        else:
            metadata[tagname] = label + value

register_track_metadata_processor(MusicBeeCompatibility().musicbee_compatibility)