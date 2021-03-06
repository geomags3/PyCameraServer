from render_modes import *

def render_with_mode(modes_ajax, sliders_ajax, main_frame, frame_background,
                     f, f1, yolo_network, rcnn_network, caffe_network, superres_network,
                     dain_network, esrgan_network, device, output_layers, classes_index, zip_obj, zip_is_opened,
                     zipped_images, server_states, started_rendering_video
):
    # YOLO Modes
    if modes_ajax["using_yolo_network"]:
        # Find all boxes with classes
        boxes, indexes, class_ids, confidences, classes_out = find_yolo_classes(
            main_frame,
            yolo_network,
            output_layers,
            int(sliders_ajax["confidenceSliderValue"])
        )
        classes_index.append(classes_out)

        # Draw boxes with labels on frame
        # Extract all image regions with objects and add them to zip
        if modes_ajax["extract_objects_yolo_mode"]:
            main_frame, zipped_images, zip_obj, zip_is_opened = extract_objects_yolo(
                main_frame,
                boxes,
                indexes,
                class_ids,
                confidences,
                zip_obj,
                zip_is_opened,
                zipped_images,
                server_states.source_mode,
                started_rendering_video,
            )

        # If it is image, close zip immediately
        if server_states.source_mode == "image" and zip_is_opened:
            zip_obj.close()

        # Prepare zip to reopening
        if server_states.source_mode == "image" and zipped_images == False:
            zipped_images = True
            zip_is_opened = False

        # Draw YOLO objects with ASCII effect
        if modes_ajax["text_render_yolo"]:
            main_frame = objects_to_text_yolo(
                main_frame,
                boxes,
                indexes,
                class_ids,
                int(sliders_ajax["asciiSizeSliderValue"]),
                int(sliders_ajax["asciiIntervalSliderValue"]),
                int(sliders_ajax["rcnnBlurSliderValue"]),
                int(sliders_ajax["asciiThicknessSliderValue"]),
            )

        # Draw YOLO objects with canny edge detection on black background
        if modes_ajax["canny_people_on_black"]:
            main_frame = canny_people_on_black_yolo(main_frame, boxes, indexes, class_ids)

        # Draw YOLO objects with canny edge detection on source colored background
        if modes_ajax["canny_people_on_background"]:
            main_frame = canny_people_on_background_yolo(main_frame, boxes, indexes, class_ids)

    # MASK R-CNN Modes
    if modes_ajax["using_mask_rcnn_network"]:
        # Find all masks with classes
        boxes, masks, labels, colors = find_rcnn_classes(main_frame, rcnn_network)

        # Convert background to grayscale and add color objects
        if modes_ajax["color_objects_on_gray"]:
            main_frame = colorizer_people_rcnn(
                main_frame,
                boxes,
                masks,
                int(sliders_ajax["confidenceSliderValue"]),
                int(sliders_ajax["rcnnSizeSliderValue"]),
                int(sliders_ajax["rcnnBlurSliderValue"]),
            )

        # Convert background to grayscale with blur and add color objects
        if modes_ajax["color_objects_on_gray_blur"]:
            main_frame = colorizer_people_with_blur_rcnn(
                main_frame,
                boxes,
                masks,
                int(sliders_ajax["confidenceSliderValue"])
            )

        # Blur background behind RCNN objects
        if modes_ajax["color_objects_blur"]:
            main_frame = people_with_blur_rcnn(
                main_frame,
                boxes,
                masks,
                labels,
                int(sliders_ajax["confidenceSliderValue"]),
                int(sliders_ajax["rcnnSizeSliderValue"]),
                int(sliders_ajax["rcnnBlurSliderValue"]),
            )

        # Draw MASK R-CNN objects with canny edge detection on black background
        if modes_ajax["extract_and_cut_background"]:
            main_frame = extract_and_cut_background_rcnn(
                main_frame,
                boxes,
                masks,
                labels,
                int(sliders_ajax["confidenceSliderValue"])
            )

        # Draw MASK R-CNN objects on animated background
        if modes_ajax["extract_and_replace_background"]:
            main_frame = extract_and_replace_background_rcnn(
                main_frame,
                frame_background,
                boxes,
                masks,
                labels,
                colors,
                int(sliders_ajax["confidenceSliderValue"]),
                int(sliders_ajax["cannyBlurSliderValue"]),
                int(sliders_ajax["cannyThresSliderValue"]),
                int(sliders_ajax["cannyThresSliderValue2"]),
                int(sliders_ajax["lineThicknessSliderValue"])
            )

            main_frame = denoise(
                main_frame,
                int(sliders_ajax["denoiseSliderValue"]),
                int(sliders_ajax["denoiseSliderValue2"]))

        # Draw MASK R-CNN objects with canny edge detection on canny blurred background
        if modes_ajax["color_canny"]:
            main_frame = color_canny_rcnn(
                main_frame,
                boxes,
                masks,
                labels,
                int(sliders_ajax["confidenceSliderValue"]),
                int(sliders_ajax["rcnnBlurSliderValue"]),
                int(sliders_ajax["cannyBlurSliderValue"]),
                int(sliders_ajax["cannyThresSliderValue"]),
                int(sliders_ajax["cannyThresSliderValue2"]),
                int(sliders_ajax["lineThicknessSliderValue"])
            )

            main_frame = denoise(
                main_frame,
                int(sliders_ajax["denoiseSliderValue"]),
                int(sliders_ajax["denoiseSliderValue2"]))

        # Draw MASK R-CNN objects with canny edge detection on source background
        if modes_ajax["color_canny_on_background"]:
            main_frame = color_canny_on_color_background_rcnn(
                main_frame,
                boxes,
                masks,
                labels,
                int(sliders_ajax["confidenceSliderValue"])
            )

    # Grayscale frame color restoration with caffe neural network
    if modes_ajax["using_caffe_network"]:
        if modes_ajax["caffe_colorization"]:
            main_frame = colorizer_caffe(caffe_network, main_frame)

    # Cartoon effect (canny, dilate, color quantization with k-means, denoise, sharpen)
    if modes_ajax["cartoon_effect"]:
        main_frame = cartoon_effect(
            main_frame,
            int(sliders_ajax["cannyBlurSliderValue"]),
            int(sliders_ajax["cannyThresSliderValue"]),
            int(sliders_ajax["cannyThresSliderValue2"]),
            int(sliders_ajax["lineThicknessSliderValue"]),
            int(sliders_ajax["colorCountSliderValue"]),
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"]),
            int(sliders_ajax["denoiseSliderValue"]),
            int(sliders_ajax["denoiseSliderValue2"])
        )

    # Pencil drawer (canny, k-means quantization to 2 colors, denoise)
    if modes_ajax["pencil_drawer"]:
        main_frame = pencil_drawer(
            main_frame,
            int(sliders_ajax["cannyBlurSliderValue"]),
            int(sliders_ajax["cannyThresSliderValue"]),
            int(sliders_ajax["cannyThresSliderValue2"]),
            int(sliders_ajax["lineThicknessSliderValue"]),
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"]),
            int(sliders_ajax["denoiseSliderValue"]),
            int(sliders_ajax["denoiseSliderValue2"])
        )

    # Pencil drawer (k-means quantization to 2 colors, denoise)
    if modes_ajax["two_colored"]:
        main_frame = two_colored(
            main_frame,
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"]),
            int(sliders_ajax["denoiseSliderValue"]),
            int(sliders_ajax["denoiseSliderValue2"])
        )

    # Super-resolution upscaler with EDSR, LapSRN and FSRCNN
    if modes_ajax["upscale_opencv"]:
        main_frame = upscale_with_superres(superres_network, main_frame)
        main_frame = sharpening(
            main_frame,
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"])
        )

    # Super-resolution upscaler with ESRGAN (FALCOON, MANGA, PSNR models)
    if modes_ajax["upscale_esrgan"]:
        main_frame = upscale_with_esrgan(esrgan_network, device, main_frame)
        main_frame = sharpening(
            main_frame,
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"])
        )

    # Draw frame with ASCII chars
    if modes_ajax["ascii_painter"]:
        main_frame = ascii_paint(
            main_frame,
            int(sliders_ajax["asciiSizeSliderValue"]),
            int(sliders_ajax["asciiIntervalSliderValue"]),
            int(sliders_ajax["asciiThicknessSliderValue"]),
            int(sliders_ajax["rcnnBlurSliderValue"]),
            attach_to_color=True
        )

    # Denoise and sharpen
    if modes_ajax["denoise_and_sharpen"]:
        main_frame = sharpening(
            main_frame,
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"]))
        main_frame = denoise(
            main_frame,
            int(sliders_ajax["denoiseSliderValue"]),
            int(sliders_ajax["denoiseSliderValue2"]))

    # Sobel filter
    if modes_ajax["sobel"]:
        main_frame = sobel(
            main_frame,
            int(sliders_ajax["denoiseSliderValue"]),
            int(sliders_ajax["denoiseSliderValue2"]),
            int(sliders_ajax["sharpenSliderValue"]),
            int(sliders_ajax["sharpenSliderValue2"]),
            int(sliders_ajax["sobelSliderValue"])
        )

    # Boost fps with Depth-Aware Video Frame Interpolation
    # Process interpolation only if user pressed START button
    frame_boost_sequence = None
    frame_boost_list = None
    if modes_ajax["boost_fps_dain"] and started_rendering_video:
        frame_boost_sequence, frame_boost_list = boost_fps_with_dain(
            dain_network, f, f1, 8, True
        )

    # Apply brightness and contrast modes_ajax for all modes
    main_frame = adjust_br_contrast(main_frame, int(sliders_ajax["contrastSliderValue"]), int(sliders_ajax["brightnessSliderValue"]))
    main_frame = adjust_saturation(main_frame, int(sliders_ajax["saturationSliderValue"]))

    return main_frame, frame_boost_sequence, frame_boost_list, classes_index, zipped_images, zip_obj, zip_is_opened