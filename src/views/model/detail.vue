<template>
  <div class="app-container">
    <p class="title">任务详情</p>
    <table class="task-detail-table">
      <tr>
        <td><span>模型名称</span>{{ task.name }}</td>
        <td><span>模型类型</span>{{ task.model_type }}</td>
        <td><span>程序格式</span>{{ task.program_info.server.format }}</td>
      </tr>
      <tr>
        <td><span>参与节点</span>{{ task.devices.split("|").length }}</td>
        <td><span>启动时间</span>{{ task.create_time }}</td>
        <td><span>训练用时</span>{{ timeTake }}</td>
      </tr>
    </table>
    <div class="chart-container">
      <!--      <span>准确率</span>-->
      <chart ref="c1" id="c1" height="100%" width="90%" :option="optionAccu"/>
    </div>
    <div class="chart-container">
      <!--      <span>Loss</span>-->
      <chart ref="c2" id="c2" height="100%" width="90%" :option="optionLoss"/>
    </div>

    <p class="title">参与节点详情</p>
    <el-table
      ref="multipleTable"
      :data="tableData"
      v-loading="listLoading"
      tooltip-effect="dark"
      style="width: 100%"
      fit
      size="mini">
      <el-table-column
        label="#"
        width="55">
        <template slot-scope="scope">
          {{ scope.$index + 1 }}
        </template>
      </el-table-column>
      <el-table-column
        prop="name"
        label="设备名称"
        align="center"
      >
      </el-table-column>
      <el-table-column
        prop="ip"
        label="IP"
        align="center"
      >
      </el-table-column>
      <el-table-column
        prop="cpu_ing"
        label="cpu使用率"
        align="center"
        show-overflow-tooltip>
      </el-table-column>
      <el-table-column
        prop="memory_ing"
        label="内存使用率"
        align="center"
        show-overflow-tooltip>
      </el-table-column>
      <el-table-column
        prop="ping"
        label="Ping"
        align="center"
        show-overflow-tooltip>
      </el-table-column>
      <el-table-column
        prop="times"
        label="迭代次数"
        align="center"
        show-overflow-tooltip>
      </el-table-column>
      <el-table-column
        label="操作"
        align="center"
        show-overflow-tooltip>
        <el-button type="warning" size="mini">停止训练</el-button>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getTask } from '@/api/all'
import Chart from '@/components/Charts/LineMarker'
import moment from 'moment'
import * as echarts from 'echarts'
import { io } from "socket.io-client";

export default {
  props: ['mid'],
  components: {Chart},
  computed: {
    timeTake () {
      return moment.duration(moment(this.currentDate).subtract(moment(this.task.create_time))).locale("zh-cn").humanize()
    }
  },
  filters: {
    statusFilter (status) {
      const statusMap = {
        published: 'success',
        draft: 'gray',
        deleted: 'danger'
      }
      return statusMap[status]
    }
  },
  data () {
    return {
      list: null,
      listLoading: false,
      task: {
        mid: '1',
        name: 'CIFAR-10',
        model_type: '图像分类',
        devices: '',
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
        create_time: '2021-04-05 16:59:12'
      },
      tableData: [
        {name: '树莓派1', ip: '192.168.1.123', cpu_ing: '75%', memory_ing: '4.2G/8G', ping: '75', uploadTimes: 5850},
        {name: '树莓派2', ip: '192.168.1.108', cpu_ing: '84%', memory_ing: '4.0G/8G', ping: '86', uploadTimes: 5765},
        {name: '树莓派3', ip: '192.168.1.201', cpu_ing: '83%', memory_ing: '4.1G/8G', ping: '68', uploadTimes: 5654},
        {name: '树莓派4', ip: '192.168.1.222', cpu_ing: '79%', memory_ing: '4.0G/8G', ping: '95', uploadTimes: 5874},
        {name: '树莓派5', ip: '192.168.1.188', cpu_ing: '76%', memory_ing: '4.2G/6G', ping: '86', uploadTimes: 5925},
      ],
      currentDate: new Date(),
      accu_iter: ['9k', '10k', '11k', '12k', '13k', '14k', '15k', '16k', '17k', '18k', '19k', '20k', '21k', '22k', '23k', '24k', '25k', '26k', '27k', '28k', '29k'],
      accu_val: [
        73.22999835014343,
        74.32000041007996,
        72.28000164031982,
        73.29999804496765,
        75.76000094413757,
        77.10999846458435,
        77.93999910354614,
        78.00999879837036,
        77.85000205039978,
        77.6199996471405,
        77.31999754905701,
        77.38999724388123,
        78.03999781608582,
        78.14000248908997,
        78.74000072479248,
        77.27000117301941,
        78.88000011444092,
        77.7999997138977,
        79.24000024795532,
        77.93999910354614,
        79.82000112533569],
      loss_iter: ['9k', '10k', '11k', '12k', '13k', '14k', '15k', '16k', '17k', '18k', '19k', '20k', '21k', '22k', '23k', '24k', '25k', '26k', '27k', '28k', '29k'],
      loss_val: [
        0.76494961977005,
        0.7429471015930176,
        0.8101270198822021,
        0.7714148163795471,
        0.697310209274292,
        0.6685596108436584,
        0.6378448009490967,
        0.6367642283439636,
        0.6355563402175903,
        0.6389819979667664,
        0.6562851667404175,
        0.6534404158592224,
        0.6434009075164795,
        0.6149821281433105,
        0.6146975755691528,
        0.6530873775482178,
        0.605922281742096,
        0.6355803608894348,
        0.5948165059089661,
        0.6367721557617188,
        0.5900737047195435
      ],
      optionAccu: {
        // backgroundColor: '#394056',
        title: {
          top: 2,
          text: '准确率',
          textStyle: {
            fontWeight: 'normal',
            fontSize: 16,
          },
          left: '1%'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            lineStyle: {
              color: '#57617B'
            }
          }
        },
        grid: {
          top: 60,
          left: '2%',
          right: '4%',
          bottom: '2%',
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: '#57617B'
            }
          },
          data: null
        }],
        yAxis: [{
          type: 'value',
          name: '(%)',
          axisTick: {
            show: false
          },
          axisLine: {
            lineStyle: {
              color: '#57617B'
            }
          },
          axisLabel: {
            margin: 10,
            textStyle: {
              fontSize: 14
            }
          },
          splitLine: {
            lineStyle: {
              color: '#57617B'
            }
          }
        }],
        series: [{
          name: '准确率',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 5,
          showSymbol: false,
          lineStyle: {
            normal: {
              width: 1
            }
          },
          areaStyle: {
            normal: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                offset: 0,
                color: 'rgba(0, 136, 212, 0.3)'
              }, {
                offset: 0.8,
                color: 'rgba(0, 136, 212, 0)'
              }], false),
              shadowColor: 'rgba(0, 0, 0, 0.1)',
              shadowBlur: 10
            }
          },
          itemStyle: {
            normal: {
              color: 'rgb(0,136,212)',
              borderColor: 'rgba(0,136,212,0.2)',
              borderWidth: 12
            }
          },
          data: null
        }]
      },
      optionLoss: {
        // backgroundColor: '#394056',
        title: {
          top: 2,
          text: 'Loss',
          textStyle: {
            fontWeight: 'normal',
            fontSize: 16,
          },
          left: '1%'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            lineStyle: {
              color: '#57617B'
            }
          }
        },
        grid: {
          top: 60,
          left: '2%',
          right: '4%',
          bottom: '2%',
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: '#57617B'
            }
          },
          data: this.loss_iter
        }],
        yAxis: [{
          type: 'value',
          axisTick: {
            show: false
          },
          axisLine: {
            lineStyle: {
              color: '#57617B'
            }
          },
          axisLabel: {
            margin: 10,
            textStyle: {
              fontSize: 14
            }
          },
          splitLine: {
            lineStyle: {
              color: '#57617B'
            }
          }
        }],
        series: [{
          name: 'Loss',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 5,
          showSymbol: false,
          lineStyle: {
            normal: {
              width: 1
            }
          },
          areaStyle: {
            normal: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                offset: 0,
                color: 'rgba(137, 189, 27, 0.3)'
              }, {
                offset: 0.8,
                color: 'rgba(137, 189, 27, 0)'
              }], false),
              shadowColor: 'rgba(0, 0, 0, 0.1)',
              shadowBlur: 10
            }
          },
          itemStyle: {
            normal: {
              color: 'rgb(137,189,27)',
              borderColor: 'rgba(137,189,2,0.27)',
              borderWidth: 12
            }
          },
          data: this.loss_val
        }]
      }
    }
  },
  watch: {
    accu_val (newVal) {
      this.optionAccu.series[0].data = this.accu_val
      this.optionAccu.xAxis[0].data = this.accu_iter
      this.$refs.c1.updateChart()
    },
    loss_val (newVal) {
      this.optionLoss.series[0].data = this.loss_val
      this.optionLoss.xAxis[0].data = this.loss_iter
      this.$refs.c2.updateChart()
    }
  },
  created () {
    this.fetchData()
  },
  mounted () {
    this.timer = setInterval(() => {
      this.currentDate = new Date()
    }, 1000)

    this.optionAccu.series[0].data = this.accu_val
    this.optionAccu.xAxis[0].data = this.accu_iter
    this.optionLoss.series[0].data = this.loss_val
    this.optionLoss.xAxis[0].data = this.loss_iter
    this.$refs.c1.updateChart()
    this.$refs.c2.updateChart()
  },
  methods: {
    fetchData () {
      this.listLoading = true
      getTask({mid: this.mid}).then(response => {
        if (response.data.result === 0 && response.data.value) {
          this.task = response.data.value.task
          this.tableData = response.data.value.devices
          this.initWebSocket()
        } else {
          this.$message({
            type: 'error',
            message: '获取任务详情失败!' + response.data.message
          })
        }
        this.listLoading = false
      }).catch(res => {
        this.$message({
          type: 'error',
          message: '获取任务详情失败! ' + res
        })
      })
    },
    initWebSocket () {
      //初始化weosocket
      this.socket = io("ws://127.0.0.1:8088/dashboard")
      this.socket.on("connect", () => {
        console.log(this.socket.id); // x8WIv7-mJelg7on_ALbx
      })
      this.socket.on("disconnect", () => {
        console.log(this.socket.id); // undefined
      })
      this.socket.emit("apply_model_info",
        {
          mid: this.task.mid,
          uids: this.task.devices.split("|")
        }
      )
      this.socket.on("push_task_info", (info) => {
        console.log(info)
        let model_info = info.model_info
        this.accu_iter = model_info.iter
        this.loss_iter = model_info.iter
        this.accu_val = model_info.accu
        this.loss_val = model_info.loss

        let device_info = info.device_info
        let newTableData = []
        for (let i = 0; i < device_info.length; i++) {
          newTableData.push(Object.assign(this.tableData[i], device_info[i]))
        }
        this.tableData = newTableData
      });
    }
  },
  beforeDestroy () {
    if (this.timer) {
      clearInterval(this.timer); // 在Vue实例销毁前，清除我们的定时器
    }
    if (this.socket) {
      this.socket.disconnect()
    }
  }
}
</script>

<style scoped>
.title {
  font-weight: bolder;
  font-size: large;
  margin-top: 0;
}

.task-detail-table {
  width: 100%;
  font-weight: bolder;
  color: #00b0e8;
  background: #cac9c63d;
  padding: 12px;
  table-layout: fixed;
}

.task-detail-table tr {
  height: 24px;
}

.task-detail-table td span {
  color: #012e55;
  margin-right: 10px;
  text-decoration: underline;
}

.chart-container {
  display: inline-block;
  position: relative;
  width: 50%;
  height: calc(30vh + 55px);
  text-align: center;
  margin-top: 10px;
}
</style>
