PLUGIN_NAME = 'Copy to Comment'
PLUGIN_AUTHOR = 'd2freak and Sophist'
PLUGIN_DESCRIPTION = '''
Some music players are unable to display the standard tags produced by Picard for Composer, Performers etc.
This plugin copies this data to the default Comment so that these players can (hopefully) display this information.
<br/><br/>
Note 1: The tags used by this plugin are only populated when you have checked Options / Metadata / Use track relationships.
<br/>
Note 2: Info copied includes ALL performance types, as well as the Composer, Producer, Mixer and so on.'''
PLUGIN_VERSION = "0.3"
PLUGIN_API_VERSIONS = ["0.15.0", "0.15.1", "0.16.0", "1.0.0", "1.1.0", "1.2.0", "1.3.0"]

from picard.metadata import register_track_metadata_processor

def populate_comment(album, metadata, trackNode, releaseNode):
    populate_comment_check(metadata, 'composer', _('Composed by'))
    populate_comment_check(metadata, 'lyricist', _('Lyrics by'))
    populate_comment_check(metadata, 'writer', _('Composed / lyrics by'))
    populate_comment_check(metadata, 'arranger', _('Arranged by'))
    populate_comment_check(metadata, 'conductor', _('Conducted by'))
    populate_comment_check(metadata, 'producer', _('Produced by'))
    populate_comment_check(metadata, 'engineer', _('Engineered by'))
    populate_comment_check(metadata, 'mixer', _('Mixed by'))
    populate_comment_check(metadata, 'remixer', _('Remixed by'))
    populate_comment_check(metadata, 'djmixer', _('DJ Mixed by'))

    for name in [i for i in metadata if i.startswith('performer:')]:
        populate_comment_check(metadata, name, name[10:].title() + ' ' + _('performed by'))

    if 'recording' in trackNode.children \
    and 'relation_list' in trackNode.recording[0].children:
        populate_comment_recording_relation_lists(metadata, trackNode.recording[0].relation_list)

def populate_comment_check(metadata, index, label):
    if not index in metadata:
        return
    tag = metadata.getall(index)
    if len(tag) == 0:
        return
    populate_comment_add(metadata, label + ": " + populate_comment_join(tag))

def populate_comment_join(text, final = ' & ', joiner = ', '):
    if len(text) == 0:
        return ''
    if len(text) == 1:
        return text[0]
    return joiner.join(text[0:len(text)-1]) + final + text[-1]

def populate_comment_add(metadata, text):
    if 'comment:' in metadata:
        metadata['comment:'] += " \n" + text
    else:
        metadata['comment:'] = text

def populate_comment_recording_relation_lists(metadata, relation_lists):
    for relation_list in relation_lists:
        if relation_list.target_type == 'work' \
        and 'relation' in relation_list.children \
        and relation_list.relation[0].type == 'performance':
            populate_comment_work_relation(metadata, relation_list.relation[0])

def populate_comment_work_relation(metadata, relation):
    work_relation_tuple = populate_comment_work_relation_tuple(relation)
    if 'work' in relation.children:
        populate_comment_work(metadata, work_relation_tuple, relation.work[0])

def populate_comment_work_relation_tuple(relation):
    if 'attribute_list' in relation.children \
    and 'attribute' in relation.attribute_list[0].children:
        attributes = relation.attribute_list[0].attribute
        atts = []
        for attribute in attributes:
            atts.append(attribute.text)
        live = 'live' in atts
        medley = 'medley' in atts
        partial = 'partial' in atts
        instrumental = 'instrumental' in atts
        cover = 'cover' in atts
        return (live, medley, partial, instrumental, cover)
    else:
        return (False, False, False, False, False)

# sequence order is defined as:
#    {live} {medley:medley including a} {partial} {instrumental} {cover} recording of
# see http://musicbrainz.org/relationship/a3005666-a872-32c3-ad06-98af558e99b0
populate_comment_work_description = {
    # (live, medley, partial, instrumental, cover): N_(u"string")
    (False, False, False, False, False): N_(u"Recording of"),
    (False, False, False, False, True): N_(u"Cover recording of"),
    (False, False, False, True, False): N_(u"Instrumental recording of"),
    (False, False, False, True, True): N_(u"Instrumental cover recording of"),
    (False, False, True, False, False): N_(u"Partial recording of"),
    (False, False, True, False, True): N_(u"Partial cover recording of"),
    (False, False, True, True, False): N_(u"Partial instrumental recording of"),
    (False, False, True, True, True): N_(u"Partial instrumental cover recording of"),
    (False, True, False, False, False): N_(u"Medley including a recording of"),
    (False, True, False, False, True): N_(u"Medley including a cover recording of"),
    (False, True, False, True, False): N_(u"Medley including an instrumental recording of"),
    (False, True, False, True, True): N_(u"Medley including an instrumental cover recording of"),
    (False, True, True, False, False): N_(u"Medley including a partial recording of"),
    (False, True, True, False, True): N_(u"Medley including a partial cover recording of"),
    (False, True, True, True, False): N_(u"Medley including a partial instrumental recording of"),
    (False, True, True, True, True): N_(u"Medley including a partial instrumental cover recording of"),
    (True, False, False, False, False): N_(u"Live recording of"),
    (True, False, False, False, True): N_(u"Live cover recording of"),
    (True, False, False, True, False): N_(u"Live instrumental recording of"),
    (True, False, False, True, True): N_(u"Live instrumental cover recording of"),
    (True, False, True, False, False): N_(u"Live partial recording of"),
    (True, False, True, False, True): N_(u"Live partial cover recording of"),
    (True, False, True, True, False): N_(u"Live partial instrumental recording of"),
    (True, False, True, True, True): N_(u"Live partial instrumental cover recording of"),
    (True, True, False, False, False): N_(u"Live medley including a recording of"),
    (True, True, False, False, True): N_(u"Live medley including a cover recording of"),
    (True, True, False, True, False): N_(u"Live medley including an instrumental recording of"),
    (True, True, False, True, True): N_(u"Live medley including an instrumental cover recording of"),
    (True, True, True, False, False): N_(u"Live medley including a partial recording of"),
    (True, True, True, False, True): N_(u"Live medley including a partial cover recording of"),
    (True, True, True, True, False): N_(u"Live medley including a partial instrumental recording of"),
    (True, True, True, True, True): N_(u"Live medley including a partial instrumental cover recording of"),
}

def populate_comment_work(metadata, tuple, work):
    if 'title' in work.children:
        work_title = _(populate_comment_work_description[tuple]) + ': ' + work.title[0].text
        populate_comment_add(metadata, work_title)
        if not tuple[-1]:
            return
        originally_by = ''
        if tuple[-1] and 'relation_list' in work.children:
            # This is a cover so try to work out who the original performers were
            for relation_list in work.relation_list:
                if relation_list.target_type == 'recording' \
                and 'relation' in relation_list.children:
                    originally_by = populate_comment_work_original_performer(relation_list.relation)
        if originally_by:
            populate_comment_add(metadata, 'Originally performed by: ' + originally_by)

def populate_comment_work_original_performer(relations):
    studio_artists = {}
    all_artists = {}
    for relation in relations:
        if relation.type == 'performance' \
        and 'target' in relation.children:
            live, medley, partial, instrumental, cover = populate_comment_work_relation_tuple(relation)
            # Since this track IS a cover we are looking for other tracks which are:
            # Full recordings (not partial) - by definition, original is full
            # Not part of a medley (obviously not original if a medley)
            # Ideally a studio recording, though original could have been live
            if not cover and not partial and not medley:
                recording_id = relation.target[0].text
                if 'recording' in relation.children \
                and 'artist_credit' in relation.recording[0].children \
                and 'name_credit' in relation.recording[0].artist_credit[0].children:
                    assert(relation.recording[0].id == recording_id)
                    recording_artist_ids = []
                    recording_artists = []
                    for name_credit in relation.recording[0].artist_credit[0].name_credit:
                        if 'artist' in name_credit.children:
                            recording_artist_ids.append(name_credit.artist[0].id)
                            if 'name' in  name_credit.artist[0].children:
                                recording_artists.append(name_credit.artist[0].name[0].text)
                    key = tuple([tuple(recording_artist_ids), tuple(recording_artists)])
                    all_artists[key] = 1 + (all_artists[key] if key in all_artists else 0)
                    if not live:
                        studio_artists[key] = 1 + (studio_artists[key] if key in studio_artists else 0)
    # We now have the set of artists against studio and all recordings. Result if:
    # 1. One studio artist
    # 2. No studio artist and one live artist
    # 3. One studio artist after eliminating artists with one recording.
    if len(studio_artists) == 1:
        return populate_comment_join(studio_artists.items()[0][0][1])
    if len(studio_artists) == 0:
        if len(all_artists) == 1 :
            return populate_comment_join(all_artists.items()[0][0][1])
        return ''
    multi_recordings = []
    for artists, count in studio_artists.iteritems():
        if count > 1:
            multi_recordings.append(artists)
    if len(multi_recordings) == 1:
        return populate_comment_join(multi_recordings[0][1])
    return populate_comment_join(
        [populate_comment_join(key[1]) for key in studio_artists.keys()],
        final = ' and by ',
        joiner = ', by ',
    )
    return ''

try:
    from picard.plugin import PluginPriority
    register_track_metadata_processor(populate_comment, priority=PluginPriority.LOW)
except ImportError:
    log.warning(
        "The %r plugin is designed to run at a specific priority,"
        "however this version of Picard does not include the priority capability"
        "and so the plugins may not run in the correct sequence and"
        "therefore may not work as you expect.",
        PLUGIN_NAME
    )
    register_track_metadata_processor(populate_comment)