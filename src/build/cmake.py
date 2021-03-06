from build.build import Build
import subprocess
import os


class Cmake(Build):
    _build_dir = 'build'

    def _clean(self):
        dest_path = self._build_path + self._build_dir
        subprocess.run(['rm', '-rf', dest_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        cwd = os.getcwd()
        os.chdir(self._build_path)
        os.makedirs(Cmake._build_dir)
        os.chdir(cwd)

        self.log('clean!')
        return True

    def _build(self):
        dest_path = self._build_path + self._build_dir
        cwd = os.getcwd()
        os.chdir(dest_path)

        ret_status = True
        not_error = subprocess.run(['cmake', '..'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not_error.returncode == 0:
            self.log('Makefile generation SUCCESS!')
            for target in self._build_targets:
                not_error = subprocess.run(['make', target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if not_error.returncode == 0:
                    self.log('target ' + target + ' build SUCCESS!')
                else:
                    self.log('target ' + target + ' build ERROR!')
                    if not self._get_interrupt_if_fail():
                        continue
                    else:
                        self.get_logger().set_execution_status(False)
                        ret_status = False
                        break
        else:
            self.log('Makefile generation ERROR!')
            self.get_logger().set_execution_status(not self._get_interrupt_if_fail())
            ret_status = self._get_interrupt_if_fail()

        os.chdir(cwd)
        return ret_status
