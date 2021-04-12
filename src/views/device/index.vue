<template>
  <div class="app-container">
    <div class="title">
      <span class="title-item">注册设备：{{ totalNum }}</span>
<!--      <span class="title-item">当前在线设备：{{ onlineDevice }}</span>-->
      <el-button style="float: right" plain size="mini" type="warning" @click="fetchData">
        <i class="el-icon-refresh" />
        刷新
      </el-button>
    </div>
    <el-card class="box-card" v-for="c in cardList">
      <div slot="header" class="clearfix">
        <span class="header-item"><span class="header-label">设备名称</span> {{ c.name }}</span>
        <span class="header-item"><span class="header-label">IP</span> {{ c.ip }}</span>
        <span class="header-item"><span class="header-label">训练任务</span> {{ c.running }}</span>
        <span class="header-item">
          <span class="header-label">状态</span>
          <el-tag effect="light" :type="c.timestamp | statusFilterTag" size="small" style="margin-left: 10px">
            {{ c.timestamp | statusFilter }}
          </el-tag>
        </span>

        <el-button style="float: right; padding: 3px 0; margin-left: 15px" type="text" @click="c.show = !c.show">
          详情<i class="el-icon-caret-bottom"></i>
        </el-button>
        <el-button style="float: right; padding: 3px 0; color: #f56c6c" type="text" @click="cancel(c.uid)">
          注销<i class="el-icon-link"></i>
        </el-button>
      </div>
      <el-collapse-transition>
        <div class="box-card-content">
<!--        <div  v-show="c.show" class="box-card-content">-->
          <table class="content-table">
            <tr>
              <td><span>CPU型号：</span>{{ c.cpu }}</td>
              <td><span>内存容量：</span>{{ c.memory }}GB</td>
              <td><span>操作系统：</span>{{ c.os }}</td>
            </tr>
            <tr>
              <td><span>CPU占用：</span>{{ c.cpu_ing }}%</td>
              <td><span>内存占用：</span>{{ c.memory_ing }}GB</td>
              <td><span>ping：</span>{{ c.ping }}ms</td>
            </tr>
          </table>
        </div>
      </el-collapse-transition>
    </el-card>

    <div class="page">
      <el-pagination
        background
        @current-change="fetchData"
        :current-page.sync="currentPage"
        layout="prev, pager, next"
        :total="totalNum">
      </el-pagination>
    </div>

  </div>
</template>

<script>
import { getDeviceList, deleteDevice } from '@/api/all'
import Table from "element-ui/lib/table";

export default {
  components: {Table},
  filters: {
    statusFilterTag (timestamp) {
      if (Date.parse(new Date()) / 1000 - timestamp > 300) {
        return "danger"
      } else {
        return "success"
      }
    },
    statusFilter(timestamp) {
      if (Date.parse(new Date()) / 1000 - timestamp > 300) {
        return "离线"
      } else {
        return "在线"
      }
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      showCards: [],
      onlineDevice: 5,
      cardList: [
        {
          uid: 1,
          name: '树莓派1',
          ip: '192.168.1.123',
          timestamp: '1617895784',
          cpu: 'ARM Cortex-A72 1.5GHz 64位四核',
          memory: '8G',
          os: 'Raspberry Pi OS',
          cpu_ing: '43%',
          memory_ing: '1.5G',
          ping: '65ms',
          show: false
        },
        {
          uid: 2,
          name: '树莓派2',
          ip: '192.168.1.108',
          timestamp: '1617895784',
          cpu: 'ARM Cortex-A72 1.5GHz 64位四核',
          memory: '8G',
          os: 'Raspberry Pi OS',
          cpu_ing: '38%',
          memory_ing: '0.8G',
          ping: '73ms',
          show: false
        },
        {
          uid: 3,
          name: '树莓派3',
          ip: '192.168.1.201',
          timestamp: '1617895784',
          cpu: 'ARM Cortex-A72 1.5GHz 64位四核',
          memory: '8G',
          os: 'Raspberry Pi OS',
          cpu_ing: '33%',
          memory_ing: '1.4G',
          ping: '60ms',
          show: false
        },
        {
          uid: 4,
          name: '树莓派4',
          ip: '192.168.1.222',
          timestamp: '1617895784',
          cpu: 'ARM Cortex-A72 1.5GHz 64位四核',
          memory: '8G',
          os: 'Raspberry Pi OS',
          cpu_ing: '42%',
          memory_ing: '1.6G',
          ping: '44ms',
          show: false
        },
        {
          uid: 5,
          name: '树莓派5',
          ip: '192.168.1.188',
          timestamp: '1617895784',
          cpu: 'ARM Cortex-A72 1.5GHz 64位四核',
          memory: '8G',
          os: 'Raspberry Pi OS',
          cpu_ing: '39%',
          memory_ing: '1.5G',
          ping: '85ms',
          show: false
        }
      ],
      timer: null,
      currentPage: 1,
      totalNum: 1
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.listLoading = true
      getDeviceList({currentPage: this.currentPage}).then(response => {
        if (response.data.result === 0) {
          this.cardList = response.data.value
          this.totalNum = response.data.count
        } else {
          this.$message({
            type: 'error',
            message: '获取设备列表失败!' + response.data.message
          })
        }
        this.listLoading = false
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '获取设备列表失败! ' + res
        })
      })
    },
    cancel (uid) {
      deleteDevice({uid: uid}).then(response => {
        if (response.data.result === 0) {
          this.$message({
            type: 'success',
            message: '注销成功'
          })
          this.fetchData()
        } else {
          this.$message({
            type: 'error',
            message: '注销失败!' + response.data.message
          })
        }
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '注销失败! ' + res
        })
      })
    }
  },
  mounted () {
    this.timer = setInterval(() => {
      this.fetchData()
    }, 3000)
  },
  beforeDestroy () {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style>
.title {
  margin-bottom: 15px;
}
.title-item {
  margin-right: 20px;
}
.header-item {
  margin-right: 25px;
}
.header-label {
  color: #00b0e8;
  font-weight: bolder;
  /*background-color: wheat;*/
}
.box-card {
  margin-bottom: 10px;
}
.box-card-content {
  padding: 20px;
}
.el-card__body {
  padding: 0;
}
.content-table {
  width: 100%;
  text-align: justify;
}
.content-table td span {
  font-weight: bold;
}
.content-row {
  margin-bottom: 5px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.page {
  text-align: center;
}
</style>
