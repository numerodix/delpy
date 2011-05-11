# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

if __name__ == '__main__': import __path__

import fnmatch
import glob
import ntpath
import os
import platform
import posixpath
import re
import subprocess
import sys
import tempfile

from delpy.lib import pythonpath
from delpy.lib import ansicolor

## Global vars

MOUNT_TABLE_S = None

## Output

def write(s):
    sys.stderr.write('%s' % s)
    sys.stderr.flush()

def write_indented(s, indent):
    indent_s = indent * 2 * ' '
    sys.stderr.write('%s%s' % (indent_s, s))
    sys.stderr.flush()

def write_next_action(s, indent=0, error=False):
    color = error and ansicolor.red or ansicolor.yellow
    prompt = error and '!!' or '>>'
    write_indented(color('%s %s ...\n' % (prompt, s)), indent)

def write_result(s, indent=0, error=False):
    color = error and ansicolor.red or ansicolor.green
    prompt = error and '!' or '*'
    write_indented(color('%s %s ...\n' % (prompt, s)), indent)

def output(s):
    sys.stdout.write('%s' % s)
    sys.stdout.flush()

## Finding files

def iglob(filepath):
    """Case insensitive globbing -> OS portable"""
    def iglob_pattern(filepath):
        """ *.RES -> *.[rR][eE][sS] """
        ifilepath = ''
        for char in filepath:
            if re.match('[a-zA-Z]', char):
                ifilepath += '[%s%s]' % (char.lower(), char.upper())
            else:
                ifilepath += char
        return ifilepath

    fp = filepath
    if platform_is_linux():
        fp = iglob_pattern(filepath)
    if platform_is_cygwin():
        drive, fp = ntpath.splitdrive(fp)
        fp = iglob_pattern(fp)
        if drive:
            fp = drive + '\\' + fp
    return glob.glob(fp)

def iglobs(filepaths):
    wglob = lambda globber,fp: globber(fp) or [fp]
    # specialize for case insensitive paths
    if path_is_icase():
        return reduce(lambda x,y: x+y, [wglob(glob.glob, fp) for fp in filepaths] or [[]])
    return reduce(lambda x,y: x+y, [wglob(iglob, fp) for fp in filepaths] or [[]])

def ifile_exists(filepath):
    # specialize for case insensitive paths
    if path_is_icase():
        if '*' in filepath or '?' in filepath:
            return glob.glob(filepath) and True or False
        return os.path.exists(filepath)
    found = iglob(filepath)
    # if no match is found, iglob returns the same file, so we have to check it
    if found:
        return os.path.exists(found[0])

def ifind(root, pat):
    fs = []
    for r, dirs, files in os.walk(root):
        fs.extend(iglob(os.path.join(r, pat)))
    return fs

def ifind_by_exts(root, exts, isort=True):
    fs = ifind(root, '*')
    exts_rx = '(?i)\.(%s)$' % '|'.join(exts)
    fs = filter(lambda x: re.search(exts_rx, x), fs)
    if isort:
        fs = sorted(fs, key=lambda x:x.lower())
    # XXX smallest first
    if not platform_is_cygwin():
        fs = sorted(fs, key=lambda x:os.path.getsize(x))
    # kill leading ./ in ./path/to/filename
    fs = map(lambda fn: re.sub('^[.][/]', '', fn), fs)
    return fs

## Tempfiles

def get_tmpdir():
    return tempfile.gettempdir()

def get_tmpfile(filename, noclobber=False):
    tmpdir = tempfile.gettempdir()
    file_src = '.%s' % filename
    fp = os.path.join(tmpdir, file_src)
    if noclobber:
        while os.path.exists(fp):
            stem, ext = os.path.splitext(fp)
            ste, id = os.path.splitext(stem)
            try:
                n = int(id[1:])
                n += 1
                ste += '.%s' % n
                stem = ste
            except ValueError:
                stem += '.2'
            fp = stem + ext
    return fp

## Platform detection

def path_join_is_winlike():
    """Detect windows path behavior"""
    return os.path.normpath(os.path.join('c:\\windows', '..\\temp')) == 'c:\\temp'

def path_is_icase():
    '''Detect path being case insensitive'''
    return os.path.normcase('a') == os.path.normcase('A')

def platform_is_cygwin():
    if re.match('(?i)^cygwin', platform.system()):
        return True

def platform_is_linux():
    if re.match('(?i)^linux', platform.system()):
        return True

def platform_is_posix():
    return platform_is_cygwin() or platform_is_linux()

## FS traversal

def safechdir(path):
    os.chdir(path or '.')

def iwalk_downto(filepath, dest):
    """Traverse from filepath down to path"""
    dirname, basename = os.path.split(filepath)
    right = basename
    while basename:
        nextbasename = os.path.basename(dirname)
        if re.match('(?i)%s' % dest, nextbasename):
            return dirname, right
        dirname, basename = os.path.split(dirname)
        right = os.path.join(basename, right)

def chmod_R(path, mode):
    for r, dirs, files in os.walk(path):
        st = os.stat(r)
        os.chmod(r, st.st_mode | mode)
        for file in files:
            fp = os.path.join(r, file)
            st = os.stat(fp)
            os.chmod(fp, st.st_mode | mode)

## Path handling

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def convert_path(path):
    if not path_join_is_winlike() and path_is_win(path):
        return path_win_to_posix(path)
    return path

def relpath(path, relative_to=None):
    if path_is_win(path):
#        if relative_to and not path_is_win(relative_to):
#            raise ValueError("Both paths must be of the same platform")
        try:
            return pythonpath.ntpath.relpath(path, start=relative_to)
        except ValueError: # when paths on different drives
            return path
    else:
#        if relative_to and path_is_win(relative_to):
#            raise ValueError("Both paths must be of the same platform")
        return pythonpath.posixpath.relpath(path, start=relative_to)

def path_is_abs(path):
    if path_is_win(path):
        return ntpath.isabs(path)
    else:
        return posixpath.isabs(path)

def path_is_win(path):
    if re.search(re.escape(ntpath.sep), path) or re.search('(?i)^[a-z]:', path):
        return True

def path_win_to_posix(path):
    return re.sub(re.escape(ntpath.sep), posixpath.sep, path)

def path_join(path_tree, path_branch):
    """Path join where Windows and Unix paths are mixed"""
    path = None
    if path_is_win(path_tree) and path_is_win(path_branch):
        path = ntpath.join(path_tree, path_branch)
        path = ntpath.normpath(path)
    if not path_is_win(path_tree) and not path_is_win(path_branch):
        path = posixpath.join(path_tree, path_branch)
        path = posixpath.normpath(path)
    if path:
        return path
    raise Exception("Could not join %s and %s" % (path_tree, path_branch))

def path_cygwin_to_win(path):
    """When running in cygwin paths passed around are posix like, convert to
    windows like

    == Case 1, path is from outside cygwin /, starts with /cygdrive/*

    1. path is
        /cygdrive/c/DOCUME~1/Owner/LOCALS~1/Temp
    2. match /cygdrive/* against mount table
        C:/cygwin/bin on /usr/bin type ntfs (binary,auto)
        C:/cygwin/lib on /usr/lib type ntfs (binary,auto)
        C:/cygwin on / type ntfs (binary,auto)
        C: on /cygdrive/c type ntfs (binary,posix=0,user,noumount,auto)
        D: on /cygdrive/d type iso9660 (binary,posix=0,user,noumount,auto)
        Z: on /cygdrive/z type hgfs (binary,posix=0,user,noumount,auto)
    3. /cygdrive/* -> c:/
        c:/DOCUME~1/Owner/LOCALS~1/Temp

    == Case 2, path is from inside cygwin /

    1. path is
        /home/Owner/thesis/code/dcc32/lib
    2. find / mount point in mount table
        C:/cygwin/bin on /usr/bin type ntfs (binary,auto)
        C:/cygwin/lib on /usr/lib type ntfs (binary,auto)
        C:/cygwin on / type ntfs (binary,auto)
        C: on /cygdrive/c type ntfs (binary,posix=0,user,noumount,auto)
        D: on /cygdrive/d type iso9660 (binary,posix=0,user,noumount,auto)
        Z: on /cygdrive/z type hgfs (binary,posix=0,user,noumount,auto)
    3. / -> c:/cygwin
        c:/cygwin/home/Owner/thesis/code/dcc32/lib
    """
    def find_mount_point(mp):
        global MOUNT_TABLE_S
        if not MOUNT_TABLE_S:
            _, MOUNT_TABLE_S = invoke('mount')
        mount_table = MOUNT_TABLE_S.split('\n')
        for mount in mount_table:
            m = re.search('^(.*) on (.*) type.*', mount)
            device, mount_point = m.group(1), m.group(2)

            m = re.search(mp, mount_point)
            if m:
                return device, m.group(0)
        raise Exception("Mount point not found: %s" % mp)

    if path_is_win(path):
        return path

    if not path_is_abs(path):
        return path.replace(posixpath.sep, ntpath.sep)

    path_new = None

    device, mount_point = find_mount_point(r'(?i)/cygdrive/[^/]+')
    if mount_point:
        # match found mount point /cygdrive/* against path
        m = re.search(mount_point, path)
        if m:
            path_new = re.sub(mount_point, device, path)

    if not path_new:
        device, mount_point = find_mount_point('^/$')
        path_new = device + path

    return re.sub('/', '\\\\\\\\', path_new)

## Writing files

def rename(src, trg):
    '''Work around retarded windows semantics'''
    if os.path.exists(trg):
        os.unlink(trg)
    os.rename(src, trg)

## Invocation

def run_win32app(msg, directory, args):
    write_next_action(msg)
    oldcwd = os.getcwd()
    try:
        safechdir(directory)
        if platform_is_linux():
            args.insert(0, 'wine')
        for (i, arg) in enumerate(args):
            if ' ' in arg or (platform_is_posix() and ';' in arg):
                # XXX if last char is a quote we assume string is quoted
                if not (arg[-1] == '"' or arg[-1] == "'"):
                    args[i] = "'%s'" % arg
        cmd = " ".join(args)
        output(' [%s] + %s\n' % (os.getcwd(), cmd))
        if 0 != os.system(cmd):
            write_result("FAILED", error=True)
            return 1
        write_result("DONE")
    finally:
        safechdir(oldcwd)

def invoke(args, cwd='.', return_all=False):
    popen = subprocess.Popen(args, cwd=cwd,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = popen.communicate()
    out = str(out).strip()
    err = str(err).strip()
    ret = popen.returncode
    if return_all:
        return ret, out, err
    if ret:
        write_result('Failed cmd: %s' % ' '.join(args), error=True)
        if err:
            write_result(err, error=True)
    return ret, out

def find_application(desc, linux, win):
    # Portability: works on linux, cygwin, win
    if platform_is_linux():
        for d in os.environ['PATH'].split(':'):
            for r in linux:
                f = os.path.join(d, r)
                if ifile_exists(f):
                    return f
    else:
        for f in win:
            if ifile_exists(f):
                return iglob(f)[0]
    write_result('Application `%s` not found' % desc, error=True)

def find_dot_tools():
    return (
            find_application('graphviz/bin/dot',
                ['dot'],
                [
                    'c:/graphviz*/bin*/dot.exe',
                    'c:/program*/graphviz*/bin*/dot.exe',
                ]),
            find_application('graphviz/bin/tred',
                ['tred'],
                [
                    'c:/graphviz*/bin*/tred.exe',
                    'c:/program*/graphviz*/bin*/tred.exe',
                ]),
            find_application('graphviz/bin/unflatten',
                ['unflatten'],
                [
                    'c:/graphviz*/bin*/unflatten.exe',
                    'c:/program*/graphviz*/bin*/unflatten.exe',
                ]),
        )

def find_pdf_reader():
    return find_application(
        'pdf viewer',
        ['okular', 'evince', 'kpdf'],
        [
            'c:/program*/foxit*/foxit*/foxit*.exe',
            'c:/program*/adobe*/reader*/reader*/acrord32.exe',
        ])
