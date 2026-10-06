"""Re-encode the Remotion renders to the delivery spec: H.264 CRF 18, yuv420p (limited range, BT.709), AAC, faststart.
Remotion's JPEG frame path yields full-range yuvj420p; some platforms mis-handle it.
usage: python encode_final.py  (reads out/_raw/*.mp4, writes out/*.mp4)"""
import glob, os, subprocess
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for src in sorted(glob.glob('out/_raw/*.mp4')):
    dst = os.path.join('out', os.path.basename(src))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', 'scale=in_range=full:out_range=tv,format=yuv420p',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-color_range', 'tv', '-colorspace', 'bt709',
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst], check=True)
    print(dst, round(os.path.getsize(dst) / 1e6, 1), 'MB')
