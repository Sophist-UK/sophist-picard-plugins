# Sophist's Picard-Plugins

Sophist is a Picard user and amateur developer of Picard enhancements and plugins.

This repo stores copies of Sophist's Picard Plugins which are (mostly) listed on the [Picard Plugins wiki page](http://musicbrainz.org/doc/MusicBrainz_Picard/Plugins) and which are licensed under GPL and are freely available for download by other Picard users.

If you have the skills, please feel free to clone this repo and submit enhancements via the GitHub Pull Request process.

##View Variables plugin
Have you ever struggled to understand what script variables are available for you to put in your tagging or file renaming scripts, or what your use of $set in tagging scripts is actually doing?

Then this plugin is for you. It add's a context (right-click) menu item which shows a dialog listing all the variables available for a file.

Download the [ZIP file here](https://github.com/Sophist-UK/Picard-Plugins/blob/master/viewvariables.zip).

##Abbreviate artist-sort
Sometimes the album artist tag has a large number of individual names listed, particularly so for classical albums.

This plugin replaces the artists forenames with their initials i.e. `Bach, Johann Sebastian` with `Bach, J. S.` and so both shortens the string and makes it more readable.

This plugin operates only on the albumartistsort and artistsort tags.

Download the [abbreviate_artistsort.py file here](https://github.com/Sophist-UK/Picard-Plugins/blob/master/abbreviate_artistsort.py).

##Copy to Comments
Some music players are unable to display the standard tags produced by Picard for Composer, Performers etc.
This plugin copies this data to the default Comment so that these players can (hopefully) display this information.

Download the [copy_to_comment.py file here](https://github.com/Sophist-UK/Picard-Plugins/blob/master/copy_to_comment.py).
