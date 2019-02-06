set(FFMPEG_FOUND FALSE)
set(FFMPEG_libavcodec_FOUND FALSE)
set(FFMPEG_libavformat_FOUND FALSE)
set(FFMPEG_libavutil_FOUND FALSE)
set(FFMPEG_libswscale_FOUND FALSE)
set(FFMPEG_libavresample_FOUND FALSE)

find_path(FFMPEG_INCLUDE_DIR NAMES "libavcodec/version.h" PATHS ${CONAN_INCLUDE_DIRS_FFMPEG})

find_library(FFMPEG_libavcodec_LIBRARY NAMES avcodec PATHS ${CONAN_LIB_DIRS_FFMPEG} NO_DEFAULT_PATH)
find_library(FFMPEG_libavformat_LIBRARY NAMES avformat PATHS ${CONAN_LIB_DIRS_FFMPEG} NO_DEFAULT_PATH)
find_library(FFMPEG_libavutil_LIBRARY NAMES avutil PATHS ${CONAN_LIB_DIRS_FFMPEG} NO_DEFAULT_PATH)
find_library(FFMPEG_libswscale_LIBRARY NAMES swscale PATHS ${CONAN_LIB_DIRS_FFMPEG} NO_DEFAULT_PATH)
find_library(FFMPEG_libavresample_LIBRARY NAMES avresample PATHS ${CONAN_LIB_DIRS_FFMPEG} NO_DEFAULT_PATH)

if(FFMPEG_INCLUDE_DIR AND FFMPEG_libavcodec_LIBRARY AND FFMPEG_libavformat_LIBRARY AND FFMPEG_libavutil_LIBRARY AND FFMPEG_libswscale_LIBRARY)
    set(FFMPEG_FOUND TRUE)
    set(FFMPEG_libavcodec_FOUND TRUE)
    set(FFMPEG_libavformat_FOUND TRUE)
    set(FFMPEG_libavutil_FOUND TRUE)
    set(FFMPEG_libswscale_FOUND TRUE)

    set(FFMPEG_INCLUDE_DIRS ${FFMPEG_INCLUDE_DIR})
    set(FFMPEG_LIBRARY_DIRS ${CONAN_LIB_DIRS_FFMPEG})
    set(FFMPEG_LIBRARIES ${FFMPEG_libavcodec_LIBRARY} ${FFMPEG_libavformat_LIBRARY} ${FFMPEG_libavutil_LIBRARY} ${FFMPEG_libswscale_LIBRARY})

    if(FFMPEG_libavresample_LIBRARY)
        set(FFMPEG_libavresample_FOUND TRUE)
        list(APPEND FFMPEG_LIBRARIES ${FFMPEG_libavresample_LIBRARY})
    endif()
endif()

message(STATUS "(FFMPEG_FOUND : ${FFMPEG_FOUND} include: ${FFMPEG_INCLUDE_DIRS}, lib: ${FFMPEG_LIBRARIES})")

mark_as_advanced(FFMPEG_INCLUDE_DIR FFMPEG_LIBRARIES)
