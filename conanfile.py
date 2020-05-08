#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import shutil
from distutils.dir_util import copy_tree

from conans import ConanFile, tools, AutoToolsBuildEnvironment


class FFmpegConan(ConanFile):
    name = "ffmpeg"
    package_revision = "-r5"
    upstream_version = "4.1"
    version = "{0}{1}".format(upstream_version, package_revision)
    tag = "20181212-32601fb"
    description = "A complete, cross-platform solution to record, convert and stream audio and video."
    url = "https://git.ircad.fr/conan/conan-ffmpeg"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "cuda": ["9.2", "10.0", "10.1", "None"],
        "shared": ["True", "False"]
    }
    default_options = tuple([
        "cuda=None",
        "shared=True"
    ])

    exports = [
        "FindFFMPEG.cmake"
    ]
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        # if 'CI' not in os.environ:
        #     os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"
        del self.settings.compiler.libcxx

    def build_requirements(self):
        if tools.os_info.linux_distro == "linuxmint":
            pack_names = [
                "libx264-dev",
                "libx265-dev"
            ]
            installer = tools.SystemPackageTool()
            for p in pack_names:
                installer.install(p)

    def system_requirements(self):
        if tools.os_info.linux_distro == "linuxmint":
            pack_names = []
            if tools.os_info.os_version.major(fill=False) == "18":
                pack_names = [
                    "libx264-148",
                    "libx265-79"
                ]
            elif tools.os_info.os_version.major(fill=False) == "19":
                pack_names = [
                    "libx264-152",
                    "libx265-146"
                ]
            installer = tools.SystemPackageTool()
            for p in pack_names:
                installer.install(p)

    def requirements(self):
        self.requires("common/1.0.0@sight/stable")

    def source(self):
        if tools.os_info.is_windows:
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-win64-dev.zip".format(self.tag))
            copy_tree("ffmpeg-{0}-win64-dev".format(self.tag), self.source_subfolder)
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-win64-shared.zip".format(self.tag))
            copy_tree("ffmpeg-{0}-win64-shared".format(self.tag), self.source_subfolder)

        elif tools.os_info.is_macos:
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-macos64-dev.zip".format(self.tag))
            copy_tree("ffmpeg-{0}-macos64-dev".format(self.tag), self.source_subfolder)
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-macos64-shared.zip".format(self.tag))
            copy_tree("ffmpeg-{0}-macos64-shared".format(self.tag), self.source_subfolder)

        elif tools.os_info.is_linux:
            tools.get("https://ffmpeg.org/releases/ffmpeg-{0}.tar.xz".format(self.upstream_version))
            os.rename("ffmpeg-{0}".format(self.upstream_version), 'ffmpeg')

    def build(self):
        #Import common flags and defines
        import common
        if tools.os_info.is_linux:
            # Build ffmpeg
            with tools.chdir('ffmpeg'):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.fpic = True
                configure_args = [
                    '--enable-gpl',
                    '--enable-libx264',
                    '--enable-libx265',
                    '--enable-nonfree'
                ]

                if self.options.shared:
                    configure_args += [
                        '--disable-static',
                        '--enable-shared'
                    ]
                else:
                    configure_args += [
                        '--enable-static',
                        '--disable-shared'
                    ]

                # Enabling gpl and non-free may be problematic if we use the built library. For now we use only the built executable, so we don't care
                # Anyway, using h264 and h265 is normally also prohibited as the codec require licensing
                if self.options.cuda != "None":
                    configure_args += [
                        '--enable-ffnvcodec',
                        '--enable-cuda',
                        '--enable-cuvid',
                        '--enable-nvenc',
                        '--enable-libnpp',
                        "--extra-cflags=-I/usr/local/cuda/include {0}".format(common.get_c_flags()),
                        '--extra-ldflags=-L/usr/local/cuda/lib64'
                    ]
                else:
                    configure_args += [
                        "--extra-cflags={0}".format(common.get_c_flags())
                    ]

                autotools.configure(
                    args=configure_args,
                    pkg_config_paths=[os.path.join(self.package_folder, 'lib', 'pkgconfig')]
                )

                autotools.make()
                autotools.install()

    def package(self):
        self.copy("FindFFMPEG.cmake", src=".", dst=".", keep_path=False)

        if not tools.os_info.is_linux:
            copy_tree(self.source_subfolder, self.package_folder)

        if tools.os_info.is_macos:
            out_bin_dir = os.path.join(self.package_folder, "bin")

            # Copy dylib as binaries want them here
            self.copy(pattern="*.dylib*", dst="lib", src=out_bin_dir, keep_path=False)

            # Make binaries executable
            os.chmod(os.path.join(out_bin_dir, 'ffmpeg'), 0o0755)
            os.chmod(os.path.join(out_bin_dir, 'ffplay'), 0o0755)
            os.chmod(os.path.join(out_bin_dir, 'ffprobe'), 0o0755)

            # Create symlink without version name for libs
            out_lib_dir = os.path.join(self.package_folder, "lib")

            for root, dir, files in os.walk(out_lib_dir):
                with tools.chdir(root):
                    for file in files:
                        match = re.match('(.*)\\..*\\.dylib', file)
                        if match and match.lastindex == 1:
                            os.symlink(file, "{0}.dylib".format(match.group(1)))

    def package_id(self):
        self.info.include_build_settings()

        if not tools.os_info.is_linux:
            del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if tools.os_info.is_linux:
            self.output.info("Using ffmpeg {0}".format(self.upstream_version))
        else:
            self.output.info("Using ffmpeg {0} build {1}".format(self.upstream_version, self.build))

        self.env_info.path.append(os.path.join(self.package_folder, 'bin'))
