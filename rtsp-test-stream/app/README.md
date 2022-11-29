This application requires a file called `video.ts` to be in the app folder,
this video file will be used as an RTSP stream for testing. 

To convert an .mp4 to .ts you can use the following ffmpeg command:

`ffmpeg -i FaceMaskedTeam.mp4 -c copy -an video.ts`
