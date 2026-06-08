import bpy 
import json
import os
import shutil
import pathlib

def configuration(json_file):
    """
    Reads and returns the contents of a JSON file as a Python dictionary.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def clean_sequencer():
    """
    Cleans the sequencer by deleting all strips in the current sequence.
    """
    bpy.ops.sequencer.select_all(action="SELECT")
    bpy.ops.sequencer.delete()

def find_sequence_editor():
    """
    Finds and returns the sequence editor area in the current window's screen.
    """
    for area in bpy.context.window.screen.areas:
        if area.type == "SEQUENCE_EDITOR":
            return area
    return None

def clean_proxies(video_folder_path):
    """
    Deletes the BL_proxy folder within the given video folder.
    """
    bl_proxy_path = os.path.join(video_folder_path, "BL_proxy")
    if os.path.exists(bl_proxy_path):
        print(f"Removing the BL_proxies folder in {bl_proxy_path}")
        shutil.rmtree(bl_proxy_path, ignore_errors=True)

def sort_list(lst):
    return sorted(lst)


def get_last_frame(media_file_path_list1, start_frame):
    if not media_file_path_list1:
        return start_frame
    
    scene = bpy.context.scene
    seq_editor = scene.sequence_editor
    if seq_editor is None:
        seq_editor = scene.sequence_editor_create()
    
    current_frame = start_frame
    
    for media_file_path in media_file_path_list1:
        strip_name = os.path.basename(media_file_path)
        movie_strip = seq_editor.sequences.new_movie(
            name=strip_name,
            filepath=media_file_path,
            channel=1,
            frame_start=current_frame,
        )
        current_frame += movie_strip.frame_final_duration
    
    return current_frame - 1  # Last frame number


def frame_all_in_sequence_editor():
    """
    Finds the SEQUENCE_EDITOR area and frames all strips by running the 'view_all' operator.
    """
    # Get the current screen
    screen = bpy.context.window.screen

    for area in screen.areas:
        if area.type == "SEQUENCE_EDITOR":
            override = {
                'window': bpy.context.window,
                'screen': screen,
                'area': area,
                'region': next(region for region in area.regions if region.type == 'WINDOW')
            }
            bpy.ops.sequencer.view_all(override)
            break


def create_transition_between_videos(media_file_path_list1, media_file_path_list2, mode):
    """
    Creates a transition between videos by adding video strips to the sequence editor based on mode.
    """
    if bpy.context.scene is None:
        print("No scene found in context.")
        return

    # Clean the sequence editor and proxies
    clean_sequencer()
    
    area = find_sequence_editor()
    if area is None:
        print("Sequence editor not found.")
        return
    
    current_frame = 1
    # media_file_path_list1 = sort_list(media_file_path_list1)
    # media_file_path_list1 = sort_list(media_file_path_list1
    sorted(media_file_path_list1)
    if media_file_path_list2:
        sorted(media_file_path_list2)

    img = bpy.data.images.load(media_file_path_list1[0])
    width = img.size[0] 
    height  = img.size[1]
    fps = bpy.context.scene.render.fps
    fps_base = bpy.context.scene.render.fps_base


    print(f"Video Width: {width}, Height: {height}")
    # Set the render resolution
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    # Set the frame rate
    bpy.context.scene.render.fps = fps
    bpy.context.scene.render.fps_base = fps_base
    start_frame = 101
    current_frame = start_frame
    #lastframe = get_last_frame(media_file_path_list1, start_frame)
    
    if mode == None:
        for index, media_file_path in enumerate(media_file_path_list1):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            strip_name = os.path.basename(media_file_path)
            with bpy.context.temp_override(area=area):
                movie_strip = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=strip_name,
                    filepath=media_file_path,
                    channel=1,
                    frame_start=current_frame,
                )
                current_frame += movie_strip.frame_final_duration
        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe

    elif mode == "Switch A by B":
        for index, media_file_path in enumerate(media_file_path_list1):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            with bpy.context.temp_override(area=area):
                movie_strip1 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"{mode}_Clip1_{index}",
                    filepath=media_file_path_list1[index],
                    channel=1,
                    frame_start=current_frame,
                )

                
                current_frame += movie_strip1.frame_final_duration
                #current_frame += max(movie_strip1.frame_final_duration, movie_strip2.frame_final_duration)
        current_frame = start_frame
        for index, media_file_path in enumerate(media_file_path_list2):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            
            with bpy.context.temp_override(area=area):
                movie_strip2 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"{mode}_Clip2_{index}",
                    filepath=media_file_path_list2[index],
                    channel=2,
                    frame_start=current_frame,
                )
                current_frame += movie_strip2.frame_final_duration

        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe


    elif mode == "Overlay":
        for index, media_file_path in enumerate(media_file_path_list1):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            with bpy.context.temp_override(area=area):
                movie_strip1 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"Overlay_Clip1_{index}",
                    filepath=media_file_path_list1[index],
                    channel=1,
                    frame_start=current_frame,
                )

                
                current_frame += movie_strip1.frame_final_duration
                #current_frame += max(movie_strip1.frame_final_duration, movie_strip2.frame_final_duration)
        current_frame = start_frame
        for index, media_file_path in enumerate(media_file_path_list2):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            
            with bpy.context.temp_override(area=area):
                movie_strip2 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"Overlay_Clip2_{index}",
                    filepath=media_file_path_list2[index],
                    channel=2,
                    frame_start=current_frame,
                )
                current_frame += movie_strip2.frame_final_duration
                bpy.context.scene.sequence_editor.active_strip = movie_strip2
                bpy.context.active_sequence_strip.blend_type = 'OVERLAY'

        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe

    elif mode == "Side by Side":
        bpy.context.scene.render.resolution_x = width * 2
        for index, media_file_path in enumerate(media_file_path_list1):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            with bpy.context.temp_override(area=area):
                movie_strip = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"SideBySide_Clip1_{index}",
                    filepath=media_file_path,
                    channel=1,
                    frame_start=current_frame,
                )
                movie_strip.transform.offset_x = width / 2

        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe
        
        for index, media_file_path in enumerate(media_file_path_list2):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            with bpy.context.temp_override(area=area):
                movie_strip = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"SideBySide_Clip2_{index}",
                    filepath=media_file_path,
                    channel=2,
                    frame_start=current_frame,
                )
                #if index == 0:
                movie_strip.transform.offset_x = -(width / 2)
                # else:
                #     movie_strip.transform.offset_x = width / 2
        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe


    elif mode == "Difference":
        for index, media_file_path in enumerate(media_file_path_list1):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            with bpy.context.temp_override(area=area):
                movie_strip1 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"{mode}_Clip1_{index}",
                    filepath=media_file_path_list1[index],
                    channel=1,
                    frame_start=current_frame,
                )

                current_frame += movie_strip1.frame_final_duration
                #current_frame += max(movie_strip1.frame_final_duration, movie_strip2.frame_final_duration)
        current_frame = start_frame
        for index, media_file_path in enumerate(media_file_path_list2):
            video_folder_path, v = os.path.split(media_file_path)
            clean_proxies(video_folder_path)
            
            with bpy.context.temp_override(area=area):
                movie_strip2 = bpy.context.scene.sequence_editor.sequences.new_movie(
                    name=f"{mode}_Clip2_{index}",
                    filepath=media_file_path_list2[index],
                    channel=2,
                    frame_start=current_frame,
                )
                current_frame += movie_strip2.frame_final_duration
                bpy.context.scene.sequence_editor.active_strip = movie_strip2
                bpy.context.active_sequence_strip.blend_type = 'DIFFERENCE'


        lastframe = current_frame - 1
        bpy.context.scene.frame_current = lastframe
    frame_all_in_sequence_editor()


def load_media_file_path_from_json(json_file):
    """
    Loads media_file_path from a JSON file.
    """
    data = configuration(json_file)
    return data.get("media_file_path")


if bpy.context.space_data is not None and bpy.context.space_data.type == "TEXT_EDITOR":
    script_path = bpy.context.space_data.text.filepath
    print("script_path filepath :", script_path)
else:
    script_path = __file__
    print("script_path __file__ :", script_path)

script_dir = pathlib.Path(script_path).resolve().parent
print(f"[pathlib] script_dir -> {script_dir}")

filepath = bpy.data.filepath
blend_opendirectory = os.path.dirname(filepath)
json_files = [pos_json for pos_json in os.listdir(blend_opendirectory) if pos_json.endswith('.json')]
print(json_files)

path_to_file = os.path.join(blend_opendirectory, json_files[0])
print(f"path_to_file -> {path_to_file}")    

json_data = configuration(path_to_file)

media_file_path_list1 = json_data.get("media_file_path_list1", [])
media_file_path_list2 = json_data.get("media_file_path_list2", [])
mode = json_data["compare_mode"]
create_transition_between_videos(media_file_path_list1, media_file_path_list2, mode)
