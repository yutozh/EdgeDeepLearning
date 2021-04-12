<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      fit
      size="mini"
      highlight-current-row
    >
      <el-table-column align="center" label="任务编号">
        <template slot-scope="scope">
          {{ (currentPage - 1 ) * 10 + scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column label="任务名称">
        <template slot-scope="scope">
          {{ scope.row.name }}
        </template>
      </el-table-column>
      <el-table-column label="开始时间" align="center">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="结束时间" align="center">
        <template slot-scope="scope">
          <i class="el-icon-time" />
          <span v-if="scope.row.status === '训练完成'">{{ scope.row.end_time }}</span>
          <span v-else> -- </span>
        </template>
      </el-table-column>

      <el-table-column label="节点数量" align="center">
        <template slot-scope="scope">
          {{ scope.row.devices }} / {{ scope.row.devices.split("|").length }}
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="任务状态" align="center">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status | statusFilter">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="220" >
        <template slot-scope="scope">
          <el-link type="success" v-show="scope.row.status === '训练停止'" @click="startT(scope.row.mid)">开始训练</el-link>
          <el-link type="warning" v-show="scope.row.status === '训练中'" @click="stopT(scope.row.mid)">停止训练</el-link>
          <el-link v-show="scope.row.status === '训练完成'" disabled>开始训练</el-link>
          <el-link type="danger" @click="deleteT(scope.row.mid)">删除任务</el-link>
          <el-link type="primary" @click="showDetail(scope.row.mid)">查看详情</el-link>
        </template>
      </el-table-column>
    </el-table>

    <div class="page">
      <el-pagination
        @current-change="fetchData"
        :current-page.sync="currentPage"
        :page-size="10"
        layout="prev, pager, next"
        :total="totalNum">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import { getTaskList, deleteTask, stopTask, startTask } from '@/api/all'

export default {
  filters: {
    statusFilter(status) {
      const statusMap = {
        '训练中': 'success',
        '训练完成': 'gray',
        '训练停止': 'danger'
      }
      return statusMap[status]
    }
  },
  data() {
    return {
      list: [
        {
          mid: 1,
          name: 'CIFAR-10 CNN',
          create_time: '2021-03-26 15:23:56',
          end_time: '2021-03-26 22:17:13',
          devices: '4/4',
          status: '训练中'
        },
        {
          mid: 2,
          name: 'CIFAR-10 CNN',
          create_time: '2021-03-26 15:23:56',
          end_time: '2021-03-26 22:17:13',
          devices: '4/4',
          status: '训练完成'
        },
        {
          mid: 3,
          name: 'CIFAR-10 CNN',
          create_time: '2021-03-26 15:23:56',
          end_time: '2021-03-26 22:17:13',
          devices: '4/4',
          status: '训练中'
        }
      ],
      listLoading: false,
      currentPage: 1,
      totalNum: 1
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      console.log("==")
      this.listLoading = true
      getTaskList({currentPage: this.currentPage}).then(response => {
        if (response.data.result === 0) {
          this.list = response.data.value
          this.totalNum = response.data.count
        } else {
          this.$message({
            type: 'error',
            message: '获取任务列表失败!' + response.data.message
          })
        }
        this.listLoading = false
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '获取任务列表失败! ' + res
        })
      })
    },
    startT (mid) {
      startTask({mid: mid}).then(response => {
        if (response.data.result === 0) {
          this.$message({
            type: 'success',
            message: '任务启动成功'
          })
          this.fetchData()
        } else {
          this.$message({
            type: 'danger',
            message: '任务启动失败!' + response.data.message
          })
        }
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '任务启动失败! ' + res
        })
      })
    },
    stopT (mid) {
      stopTask({mid: mid}).then(response => {
        if (response.data.result === 0) {
          this.$message({
            type: 'success',
            message: '任务停止成功'
          })
          this.fetchData()
        } else {
          this.$message({
            type: 'danger',
            message: '任务停止失败!' + response.data.message
          })
        }
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '任务停止失败! ' + res
        })
      })
    },
    deleteT (mid) {
      deleteTask({mid: mid}).then(response => {
        if (response.data.result === 0) {
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.fetchData()
        } else {
          this.$message({
            type: 'danger',
            message: '删除失败!' + response.data.message
          })
        }
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '删除失败! ' + res
        })
      })
    },
    showDetail (mid) {
      this.$router.push("detail/" + mid)
    }
  }
}
</script>

<style scoped>
.el-link {
  margin-right: 6px;
}
.page {
  text-align: center;
}
</style>
