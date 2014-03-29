PLUGIN_NAME = 'Copy to Comment'
PLUGIN_AUTHOR = 'd2freak and Sophist'
PLUGIN_DESCRIPTION = '''
Some music players are unable to display the standard tags produced by Picard for Composer, Performers etc.
This plugin copies this data to the default Comment so that these players can (hopefully) display this information.
<br/><br/>
Note 1: The tags used by this plugin are only populated when you have checked Options / Metadata / Use track relationships.
<br/>
Note 2: Info copied includes ALL performance types, as well as the Composer, Producer, Mixer and so on.'''
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["1.2"]

from picard.metadata import register_track_metadata_processor

def populate_comment(tagger, metadata, track, release):
    _comment_add(metadata, 'composer', _('Composed by'))
    _comment_add(metadata, 'arranger', _('Arranged by'))
    _comment_add(metadata, 'conductor', _('Conducted by'))
    _comment_add(metadata, 'lyricist', _('Lyrics by'))
    _comment_add(metadata, 'producer', _('Produced by'))
    _comment_add(metadata, 'mixer', _('Mixed by'))
    _comment_add(metadata, 'remixer', _('Remixed by'))
    _comment_add(metadata, 'djmixer', _('DJ Mixed by'))
    _comment_add(metadata, 'engineer', _('Engineered by'))

    for ix in [i for i in metadata if i.startswith('performer:')]:
        _comment_add(metadata, ix, ix[10:].title() + ' ' + _('performed by'))

def _comment_add(metadata, index, label):
    if not index in metadata:
        return
    tag = metadata.getall(index)
    if len(tag) == 0:
        return
    if len(tag) > 1:
        value = ', '.join(tag[0:len(tag)-1]) + ' & ' + tag[-1]
    else:
        value = tag[0]
    if 'comment:' in metadata:
        metadata['comment:'] += " \n" + label + ": " + value
    else:
        metadata['comment:'] = label + ": " + value

register_track_metadata_processor(populate_comment)