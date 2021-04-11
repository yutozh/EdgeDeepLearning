<template>
  <div class="app-container">
    <el-form ref="form" :model="form" label-width="160px" size="mini" style="width: 90%;">
      <el-form-item label="模型名称">
        <el-input v-model="form.name" style="width: 550px;"/>
      </el-form-item>
      <el-form-item label="模型类型">
        <el-select v-model="form.type" placeholder="根据模型输入数据选择">
          <el-option label="图像分类" value="图像分类"/>
          <el-option label="文本" value="文本"/>
          <el-option label="语音" value="语音"/>
          <el-option label="其他" value="其他"/>
        </el-select>
      </el-form-item>

      <el-form-item label="服务端模型程序上传">
        <el-form :inline="true" class="server-form">
          <el-form-item label="程序形式：" size="mini">
            <el-radio-group v-model="form.program_info.server.format" class="radio-group">
              <el-radio border label="Docker镜像"/>
              <el-radio border label="压缩包"/>
              <el-radio border label="其他"/>
            </el-radio-group>
          </el-form-item>

          <br>
          <el-form-item v-if="form.program_info.server.format !== 'Docker镜像'" label="程序文件：">
            <el-upload
              class="upload-demo"
              action="https://jsonplaceholder.typicode.com/posts/"
              :on-success="handleUploadSuccess(form.program_info.server)"
              :before-remove="beforeRemove"
            >
              <el-button size="mini" type="primary">点击上传</el-button>
              <!--          <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>-->
            </el-upload>
          </el-form-item>

          <el-form-item v-else label="镜像地址：">
            <el-input size="mini" v-model="form.program_info.server.path" style="width: 350px;"/>
          </el-form-item>
        </el-form>
      </el-form-item>

      <el-form-item label="客户端模型程序上传">
        <el-form :inline="true" class="client-form" v-for="(form_item, index) in form.program_info.client">
          <div class="less-btn" v-if="index > 0">
            <el-button circle type="danger" @click="deleteClient(index)">
              <i class="el-icon-minus"></i>
            </el-button>
            <span style="margin-left: 5px">删除</span>
          </div>

          <el-form-item label="适用环境：" size="mini">
            <el-select v-model="form_item.object" placeholder="模型适用环境">
              <el-option label="树莓派" value="树莓派"/>
              <el-option label="安卓手机" value="安卓手机"/>
              <el-option label="安卓车载设备" value="安卓车载设备"/>
              <el-option label="IOS设备" value="IOS设备"/>
            </el-select>
          </el-form-item>
          <br>
          <el-form-item label="程序形式：" size="mini">
            <el-radio-group v-model="form_item.format" class="radio-group" label="形式">
              <el-radio border label="Docker镜像">Docker镜像</el-radio>
              <el-radio border label="压缩包">压缩包</el-radio>
              <el-radio border label="其他">其他</el-radio>
            </el-radio-group>
          </el-form-item>
          <br>

          <el-form-item v-if="form_item.format !== 'Docker镜像'" label="程序文件：">
            <el-upload
              class="upload-demo"
              action="https://jsonplaceholder.typicode.com/posts/"
              :on-success="handleUploadSuccess(form_item)"
              :before-remove="beforeRemove"
            >
              <el-button size="mini" type="primary">点击上传</el-button>
              <!--          <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>-->
            </el-upload>
          </el-form-item>

          <el-form-item v-else label="镜像地址：" size="mini">
            <el-input size="mini" v-model="form_item.path" style="width: 350px"/>
          </el-form-item>

          <br>
          <el-form-item label="启动命令：" size="mini">
            <el-input size="mini" v-model="form_item.cmd" style="width: 350px"/>
          </el-form-item>


        </el-form>

        <div class="more-btn">
          <el-button circle type="primary" @click="addClient">
            <i class="el-icon-plus"></i>
          </el-button>
          <span style="margin-left: 5px">添加...</span>
        </div>

      </el-form-item>


      <el-form-item label="设备选择" style="margin-bottom: 1px" class="device-table">
        <el-link @click="fetchDevice" type="primary">点击选择</el-link>
        <p>已选择{{ form.multipleSelection.length }}台设备</p>
      </el-form-item>
      <div style="text-align: right">
        <el-button size="small" type="primary" @click="onSubmit">创建训练任务</el-button>

      </div>
    </el-form>


    <el-dialog title="设备选择" :visible.sync="dialogTableVisible" width="70%">
      <div style="text-align: right">
        <el-checkbox-group v-model="deviceCheckList">
          <el-checkbox size="mini" label="移动设备" name="type"/>
          <el-checkbox size="mini" label="物联网设备" name="type"/>
          <el-checkbox size="mini" label="高性能设备" name="type"/>
          <el-checkbox size="mini" label="低延迟设备" name="type"/>
        </el-checkbox-group>
      </div>


      <el-table
        ref="multipleTable"
        v-loading="deviceListLoading"
        :data="tableData"
        tooltip-effect="dark"
        style="width: 100%"
        fit
        size="mini"
        @selection-change="handleSelectionChange">
        <el-table-column
          type="selection"
          width="55">
        </el-table-column>
        <el-table-column
          prop="name"
          align="center"
          label="设备名称">
        </el-table-column>
        <el-table-column
          prop="ip"
          align="center"
          label="IP">
        </el-table-column>
        <el-table-column
          prop="cpu"
          align="center"
          label="cpu型号"
          show-overflow-tooltip>
        </el-table-column>
        <el-table-column
          align="center"
          label="cpu负载"
          show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.cpu_ing }}%
          </template>
        </el-table-column>
        <el-table-column
          align="center"
          label="总内存"
          show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.memory }}GB
          </template>
        </el-table-column>
        <el-table-column
          align="center"
          label="已使用内存"
          show-overflow-tooltip>
          <template slot-scope="scope">
            {{ scope.row.memory_ing }}GB
          </template>
        </el-table-column>

        <el-table-column
          prop="data_meta"
          align="center"
          label="数据类型"
          show-overflow-tooltip>
        </el-table-column>
      </el-table>
      <div class="page">
        <el-pagination
          :current-page="currentPage"
          :page-size="5"
          layout="prev, pager, next"
          :total="totalNum">
        </el-pagination>
      </div>
      <div style="text-align: right">
        <span style="margin-right: 10px">已选择{{ form.multipleSelection.length }}台设备</span>
        <el-button size="small" type="primary" @click="dialogTableVisible=false">确定</el-button>
      </div>

    </el-dialog>
  </div>
</template>

<script>
import { addTask, getDeviceList } from '@/api/all'

export default {
  data () {
    return {
      form: {
        name: '',
        type: '',
        program_info: {
          server: {
            format: 'Docker镜像',
            path: '',
            cmd: ''
          },
          client: [
            {
              object: '',
              format: 'Docker镜像',
              path: '',
              cmd: ''
            }
          ]
        },
        multipleSelection: []
      },
      tableData: [
        // {
        //   uid: '1',
        //   name: "树莓派1",
        //   ip: "192.168.1.123",
        //   cpu: "ARM Cortex-A72 1.5GHz 64位四核",
        //   memory: "8G",
        //   data_type: "CIFAR-10 图像"
        // }
      ],
      deviceListLoading: false,
      currentPage: 1,
      totalNum: 1,
      deviceCheckList: [],
      dialogTableVisible: false,
    }
  },
  methods: {
    addClient () {
      this.form.program_info.client.push({
        object: '',
        format: 'Docker镜像',
        path: '',
        cmd: ''
      })
    },
    deleteClient (id) {
      this.form.program_info.client.splice(id, 1)
    },
    fetchDevice () {
      this.dialogTableVisible = true
      this.deviceListLoading = true
      getDeviceList({currentPage: this.currentPage}).then(response => {
        if (response.data.result === 0) {
          this.tableData = response.data.value
          this.totalNum = response.data.count
        } else {
          this.$message({
            type: 'danger',
            message: '获取设备列表失败!' + response.data.message
          })
        }
        this.deviceListLoading = false
      })
    },
    onSubmit () {
      addTask(this.form).then(response => {
        if (response.data.result === 0) {
          let device_success = response.data.value
          this.$message({
            type: 'success',
            message: `创建任务成功, 启动${device_success}台设备`
          })
        } else {
          this.$message({
            type: 'danger',
            message: '创建任务失败!' + response.data.message
          })
        }
      }).catch(res => {

      })
    },
    onCancel () {
      this.$message({
        message: 'cancel!',
        type: 'warning'
      })
    },
    handleRemove (file, fileList) {
      console.log(file, fileList);
    },
    beforeRemove (file, fileList) {
      return this.$confirm(`确定移除 ${file.name}？`);
    },
    handleSelectionChange (val) {
      let uids = []
      for (let i of val) {
        uids.push(i.uid)
      }
      this.form.multipleSelection = uids;
    },
    handleUploadSuccess (item) {

    }
  }
}
</script>

<style>
.device-table table th {
  padding: 0 !important;
}

.client-form .el-form-item__label {
  color: #4e6ba5 !important;
}

.server-form .el-form-item__label {
  color: #4a998a;
}
</style>

<style scoped>
.line {
  text-align: center;
}

.el-checkbox {
  margin-right: 18px;
}


.server-form {
  background-color: #4acb880f;
  padding: 20px;
  width: 80%;
  margin-bottom: 10px;
}

.client-form {
  background-color: #5faeff0f;
  padding: 20px;
  width: 80%;
  margin-bottom: 10px;
}

.client-form .el-form-item {
  margin-bottom: 8px !important;
}

.more-btn {
  margin-top: 5px;
  margin-bottom: 5px;
}

.less-btn {
  display: inline-block;
  float: right;
}

span {
  color: #606266;
}
</style>

