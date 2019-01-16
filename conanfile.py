#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from distutils.dir_util import copy_tree

from conans import ConanFile, tools, AutoToolsBuildEnvironment


class FFmpegConan(ConanFile):
    name = "ffmpeg"
    version = "4.1"
    tag = "20181212-32601fb"
    description = "A complete, cross-platform solution to record, convert and stream audio and video."
    url = "https://git.ircad.fr/conan/conan-ffmpeg"
    license = "LGPL"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "use_cuda": [True, False]
    }
    default_options = "use_cuda=False"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        if 'CI' not in os.environ:
            os.environ["CONAN_SYSREQUIRES_MODE"] = "verify"
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

    def source(self):
        if tools.os_info.is_windows:
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-win64-static.zip".format(self.tag))
            os.rename("ffmpeg-{0}-win64-static".format(self.tag), self.source_subfolder)

        elif tools.os_info.is_macos:
            tools.get("https://conan.ircad.fr/artifactory/list/data/ffmpeg-{0}-macos64-static.zip".format(self.tag))
            os.rename("ffmpeg-{0}-macos64-static".format(self.tag), self.source_subfolder)

        elif tools.os_info.is_linux:
            tools.get("https://ffmpeg.org/releases/ffmpeg-{0}.tar.xz".format(self.version))
            os.rename("ffmpeg-{0}".format(self.version), 'ffmpeg')

    def build(self):
        if tools.os_info.is_linux:
            # Build ffmpeg
            with tools.chdir('ffmpeg'):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.fpic = True

                # Enabling gpl and non-free may be problematic if we use the built library. For now we use only the built executable, so we don't care
                # Anyway, using h264 and h265 is normally also prohibited as the codec require licensing
                if self.options.use_cuda:
                    autotools.configure(
                        args=[
                            '--enable-gpl',
                            '--enable-libx264',
                            '--enable-libx265',
                            '--enable-ffnvcodec',
                            '--enable-cuda',
                            '--enable-cuvid',
                            '--enable-nvenc',
                            '--enable-nonfree',
                            '--enable-libnpp'
                        ],
                        pkg_config_paths=[os.path.join(self.package_folder, 'lib', 'pkgconfig')]
                    )
                else:
                    autotools.configure(
                        args=[
                            '--enable-gpl',
                            '--enable-libx264',
                            '--enable-libx265',
                            '--enable-nonfree'
                        ]
                    )
                autotools.make()
                autotools.install()

    def package(self):
        if not tools.os_info.is_linux:
            copy_tree(self.source_subfolder, self.package_folder)

    def package_id(self):
        self.info.include_build_settings()

        if not tools.os_info.is_linux:
            del self.info.settings.compiler

    def package_info(self):
        if tools.os_info.is_linux:
            self.output.info("Using ffmpeg {0}".format(self.version))
        else:
            self.output.info("Using ffmpeg {0} build {1}".format(self.version, self.build))

        self.env_info.path.append(os.path.join(self.package_folder, 'bin'))
