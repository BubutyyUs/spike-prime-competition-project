def calibrate_black_line():
    hub.light_matrix.write("B")
    wait_for_button_press()
    black_value = read_average_light()

    hub.light_matrix.write("F")
    wait_for_button_press()
    floor_value = read_average_light()

    target = black_value
    threshold_black = black_value + 10

    hub.light_matrix.write("OK")
    wait_for_seconds(0.5)
    hub.light_matrix.off()

    return target, threshold_black
