#!python
autoplay = True
verbose = True
vPlayer = "APPDIR:mplayer"
vPlayerArgs = "-quiet -really-quiet -forceidx -framedrop -cache 8192"
sPlayer = "APPDIR:ffplay"
sPlayerArgs = "-loglevel quiet -infbuf -skip_loop_filter all -skip_frame noref"

twitchQualityWeight = [
	"480p30",
	"360p30",
	"160p30",
	"720p60",
	"720p30",
	"chunked",
	"audio_only"
]

mixerQualityWeight = [
	"480p",
	"320p",
	"160p",
	"720p",
	"1080p"
]

vimeoQualityWeight = [
	"360p",
	"240p",
	"480p",
	"540p",
	"720p",
	"1080p"
]

dailymotionQualityWeight = [
	"480",
	"380",
	"240",
	"144"
	"720",
	"1080"
]