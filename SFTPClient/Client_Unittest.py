#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, call, ANY

# fix for running as script?
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import SFTPClient
from SFTPClient.Client import SFTP


class Test_Client(unittest.TestCase):
    def setUp(self):
        self.local_directory = MagicMock()
        SFTP.connection = MagicMock()
        SFTP.initiate_connection = MagicMock()
        SFTPClient.Client.os.path.isfile = MagicMock()
        SFTPClient.Client.os.path.isdir = MagicMock()
        SFTPClient.Client.tempfile.gettempdir = MagicMock()
        SFTPClient.Client.os.mkdir = MagicMock()
        SFTPClient.Client.os.path.join = MagicMock()
        SFTPClient.Client.os.path.exists = MagicMock()
        SFTPClient.Client.os.rename = MagicMock()
        SFTPClient.Client.os.remove = MagicMock()
        SFTPClient.Client.shutil.rmtree = MagicMock()
        self.myClass = SFTP("hostname", "username", "password", "public_key")

    def tearDown(self):
        pass


class Testis_connected(Test_Client):
    def test_is_connected(self):
        # setup
        self.myClass.connection.listdir.return_value = True
        # actual
        actual = self.myClass.is_connected()
        # verify
        self.myClass.connection.listdir.assert_called_once_with()
        self.assertTrue(actual)

    def test_Test_Client1(self):
        # setup
        self.myClass.connection.listdir.return_value = False
        # actual
        actual = self.myClass.is_connected()
        # verify
        self.myClass.connection.listdir.assert_called_once_with()
        self.assertFalse(actual)


class Testping(Test_Client):
    def test_ping(self):
        # setup
        self.myClass.connection.listdir.return_value = True
        # actual
        actual = self.myClass.ping("")
        # verify
        self.myClass.connection.listdir.assert_called_once_with()
        self.assertEqual(actual, "pong")

    def test_ping1(self):
        # setup
        self.myClass.connection.listdir.return_value = False
        # actual
        actual = self.myClass.ping("")
        # verify
        self.myClass.connection.listdir.assert_called_once_with()
        self.assertEqual(actual, "nothing happened")


class Testls(Test_Client):
    def test_ls(self):
        # actual
        actual = self.myClass.ls([])
        # verify
        self.myClass.connection.listdir.assert_called_once_with()
        self.assertTrue(actual)

    def test_ls1(self):
        # actual
        actual = self.myClass.ls(["car"])
        # verify
        self.myClass.connection.listdir.assert_called_once_with(("car"))
        self.assertTrue(actual, "car")

    def test_ls2(self):
        # verify
        self.assertRaises(TypeError, self.myClass.ls, ['car', 'boat'])

    def test_ls3(self):
        # verify
        self.assertRaises(TypeError, self.myClass.ls, ['0xdeadbeef', '0xdeadbeef', '0xdeadbeef'])

    def test_ls_l1(self):
        # actual
        actual = self.myClass.ls(['-l'])
        # verify
        self.myClass.connection.listdir_attr.assert_called_once_with()

    def test_ls_l2(self):
        # actual
        actual = self.myClass.ls(['-l', 'testdir'])
        # verify
        self.myClass.connection.listdir_attr.assert_called_once_with('testdir')

    def test_ls_nonexistent_dir(self):
        # setup
        self.myClass.connection.listdir.side_effect = TypeError("Usage: ls [-l] [<dir_path>]")
        # verify
        self.assertRaises(TypeError, self.myClass.ls, ['0xdeadbeef'])

    def test_ls_l_nonexistent_dir(self):
        # setup
        self.myClass.connection.listdir_attr.side_effect = TypeError("Usage: ls [-l] [<dir_path>]")
        # verify
        self.assertRaises(TypeError, self.myClass.ls, ['-l', '0xdeadbeef'])


class Testchmod(Test_Client):
    def test_chmod(self):
        # actual
        self.myClass.chmod(('car', 2))
        # verify
        self.myClass.connection.chmod.assert_called_once_with('car', 2)

    def test_chmod1(self):
        # verify
        self.assertRaises(TypeError, self.myClass.chmod, ['car', 'boat', 'train'])


class Testrm(Test_Client):
    def test_rm(self):
        # verify
        self.assertRaises(TypeError, self.myClass.rm, "Usage: rm [filename | path/to/filename]")

    def test_rm1(self):
        # setup
        self.myClass.connection.isdir.return_value = True
        # actual
        self.myClass.rm("f")
        # verify
        self.myClass.connection.remove.assert_called_once_with("f")

    def test_rm2(self):
        # setup
        self.myClass.connection.isdir.return_value = False
        # actual
        self.myClass.rm("f")
        # verify
        self.assertRaises(TypeError, self.myClass.rm, "Usage: rm [filename | path/to/filename]")


class Testmkdir(Test_Client):
    def test_mkdir(self):
        # verify
        self.assertRaises(TypeError, self.myClass.mkdir, "Usage: mkdir [dirname | path/to/dirname]")

    def test_mkdir1(self):
        # actual
        self.myClass.mkdir("/")
        # verify
        self.myClass.connection.makedirs.assert_called_once_with("/", mode=775)


class Testget(Test_Client):
    def test_get(self):
        # verify
        self.assertRaises(TypeError, self.myClass.get, "get() takes 1 or 2 arguments ("" given)")

    def test_get1(self):
        # setup
        self.myClass.connection.isfile.return_value = True
        # actual
        self.myClass.get("1")
        # verify
        self.myClass.connection.get("1", "downloads")


@patch("SFTPClient.Client.os.getcwd", autospec=True)
@patch("SFTPClient.Client.os.listdir", autospec=True)
class Testlsl(Test_Client):
    def test_lsl(self, mocklistdir, mockgetcwd):
        # setup
        mockgetcwd.return_value = "/Users/myCurrentDirectory"
        mocklistdir.side_effect = iter(["file1"])
        # actual
        self.myClass.lsl("args")
        # verify
        mocklistdir.assert_called_once_with("/Users/myCurrentDirectory")


class Testput(Test_Client):
    def test_put_file_not_found(self):
        SFTPClient.Client.os.path.isfile.return_value = False
        SFTPClient.Client.os.path.isdir.return_value = False
        with self.assertRaises(FileNotFoundError):
            self.myClass.put(['test.file'])

    def test_put_file(self):
        SFTPClient.Client.os.path.isfile.return_value = True
        SFTPClient.Client.os.path.isdir.return_value = False
        self.myClass.put(['test.file'])
        self.myClass.connection.put.assert_called_once_with('test.file', preserve_mtime=True)

    def test_put_dir(self):
        SFTPClient.Client.os.path.isfile.return_value = False
        SFTPClient.Client.os.path.isdir.return_value = True
        with self.assertRaises(IOError):
            self.myClass.put(['test_dir'])

    def test_put_file_path(self):
        SFTPClient.Client.os.path.isfile.return_value = True
        SFTPClient.Client.os.path.isdir.return_value = False
        self.myClass.put(['-t', 'random_path/to_the', 'local/file.txt'])
        self.myClass.connection.put.assert_called_once_with('local/file.txt', 'random_path/to_the/file.txt',
                                                            preserve_mtime=True)


class Testcp(Test_Client):
    def test_cp_one_arg(self):
        # verify that a TypeError is raised when only 1 argument is passed
        self.assertRaises(TypeError, self.myClass.cp, ['arg1'])
    
    def test_cp_three_arg(self):
        # verify that a TypeError is raised when too many arguments are passed
        self.assertRaises(TypeError, self.myClass.cp, ['arg1', 'arg2', 'arg3'])
    
    def test_cp_src_not_found(self):
        # verify that an IOError is raised when a non-existent source directory is passed
        self.myClass.connection.exists.side_effect = [False, False]
        self.assertRaises(IOError, self.myClass.cp, ['test.dir', 'test.dir-copy'])

    def test_cp_dst_file_exists(self):
        # verify that an IOError is raised when an existing destination file is passed
        self.myClass.connection.exists.side_effect = [True, True, True]
        self.myClass.connection.isdir.return_value = False
        self.myClass.connection.isfile.return_value = True
        self.assertRaises(IOError, self.myClass.cp, ['test.dir', 'test.file'])
    
    def test_cp_dir_valid(self):
        # setup
        self.myClass.connection.exists.side_effect = [True, False, False, False]
        self.myClass.connection.isdir.return_value = True
        self.myClass.connection.isfile.return_value = False
        SFTPClient.Client.tempfile.gettempdir.return_value = '/tmp'
        self.myClass.connection.listdir.return_value = ['something']
        SFTPClient.Client.os.path.join.side_effect = ['test.dir-copy/test.dir', '/tmp/test.dir', '/tmp/test.dir-copy', 'test.dir-copy', '/tmp/test.dir-copy', '/tmp/test.dir']
        SFTPClient.Client.os.path.exists.side_effect = [True, False]
        # actual
        self.myClass.cp(['test.dir', 'test.dir-copy'])
        # verify
        self.myClass.connection.get_r.assert_called_once_with('test.dir', '/tmp', preserve_mtime=True)
        self.myClass.connection.mkdir.assert_called_once_with('test.dir-copy')
        self.myClass.connection.put_r.assert_called_once_with('/tmp/test.dir', 'test.dir-copy', preserve_mtime=True)
        SFTPClient.Client.shutil.rmtree.assert_called_once_with('/tmp/test.dir')

    def test_cp_dir_nested(self):
        # setup
        self.myClass.connection.exists.side_effect = [True, True, False, False]
        self.myClass.connection.isdir.return_value = True
        self.myClass.connection.isfile.return_value = False
        SFTPClient.Client.tempfile.gettempdir.return_value = '/tmp'
        self.myClass.connection.listdir.return_value = ['something']
        SFTPClient.Client.os.path.join.side_effect = ['test.dir/test.dir-copy', '/tmp/test.dir', 'test.dir-copy', 'test.dir-copy', '/tmp/test.dir', '/tmp/test.dir']
        SFTPClient.Client.os.path.exists.side_effect = [True, False]
        # actual
        self.myClass.cp(['test.dir', 'test.dir-copy'])
        # verify
        self.myClass.connection.get_r.assert_called_once_with('test.dir', '/tmp', preserve_mtime=True)
        self.myClass.connection.mkdir.assert_called_once_with('test.dir-copy')
        self.myClass.connection.put_r.assert_called_once_with('/tmp/test.dir', 'test.dir-copy', preserve_mtime=True)
        SFTPClient.Client.shutil.rmtree.assert_called_once_with('/tmp/test.dir')


class Testcp_r(Test_Client):
    def test_cp_r_one_arg(self):
        # verify that a TypeError is raised when only 1 argument is passed
        self.assertRaises(TypeError, self.myClass.cp_r, ['arg1'])
    
    def test_cp_r_three_arg(self):
        # verify that a TypeError is raised when too many arguments are passed
        self.assertRaises(TypeError, self.myClass.cp_r, ['arg1', 'arg2', 'arg3'])
    
    def test_cp_r_src_not_found(self):
        # setup the exists() method to return False, and then False (invalid src, valid dst)
        self.myClass.connection.exists.side_effect = [False, False]
        # verify that an IOError is raised when a non-existent source directory is passed
        self.assertRaises(IOError, self.myClass.cp_r, ['test.dir', 'test.dir-copy'])

    def test_cp_r_dst_file_exists(self):
        # setup the exists() method to return True, and then True (valid src, invalid dst)
        self.myClass.connection.exists.side_effect = [True, True]
        self.myClass.connection.isfile.return_value = True
        # verify that an IOError is raised when an existing destination file is passed
        self.assertRaises(IOError, self.myClass.cp_r, ['test.dir', 'test.file'])

    def test_cp_r_dir_valid(self):
        # setup the exists() method to return True, and then False (valid src, valid dst)
        self.myClass.connection.exists.side_effect = [True, False]
        # actual
        self.myClass.cp_r(['test.dir', 'test.dir-copy'])
        # verify
        self.myClass.connection.execute.assert_called_once_with('cp -Rp test.dir test.dir-copy')


@patch("builtins.exit", autospec=True)
class TestcloseAndExit(Test_Client):
    def test_close(self, mockexit):
        # actual
        self.myClass.close("args")
        #verify
        self.myClass.connection.close.assert_called_once_with()
        mockexit.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
