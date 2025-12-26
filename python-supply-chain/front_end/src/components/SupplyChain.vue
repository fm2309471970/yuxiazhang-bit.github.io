<template>

  <div class="container">
    <!-- 输入框展示 -->
      <div class="input_container">
        <div class="pack_input">
          <el-input v-model="pack_name" placeholder="请输入包名" style="width:300px"></el-input>
          <el-button type="success" @click="search_version">搜索</el-button>
        </div>
        <div class="vers_select">
          <!-- 版本选择 -->
      <el-select v-model="version" class="m-2" placeholder="请选择软件包版本" @change="get_extra" size="large">
          <el-option
          v-for="item in versions"
          :key="item"
          :label="item"
          :value="item"
          />
      </el-select>
        </div>
        <div class="extra_select">
<!-- extra选择 -->
      <el-select v-model="extra" class="m-2" placeholder="请选择extra" size="large">
        <!-- <el-option label="请选择" value=""></el-option> -->
          <el-option
          v-for="item in extras"
          :key="item"
          :label="item"
          :value="item"
          />
          
          <!-- <el-option label="不需要extra" value="" v-if="version!==''" :key="version"></el-option> -->
      </el-select>
      <el-button type="success" @click="supply">绘图</el-button>
        </div>

      
      
      
      </div>
      <div class="output_container">
        <!-- 数据展示区 -->
        <div class="static_container">
           <div class="common_static">
              <h1>普通数据展示区</h1>
           </div>
           <div class="cve_static">
              <!-- <h1>cve数据</h1> -->
              <el-select v-model="selectedCveNo" placeholder="请选择CVE编号" @change="handleSelectChange">
                <el-option v-for="item in show_cve_list" :key="item.cve_no" :label="item.cve_no" :value="item.cve_no"></el-option>
              </el-select>
              <div>
                <p><b>编号</b>：{{ selectedCve.cve_no }}</p>
                <p><b>创建时间</b>：{{ selectedCve.cve_create_time }}</p>
                <p><b>CNA</b>：{{ selectedCve.cve_cna }}</p>
                <p><b>描述</b>：{{ selectedCve.cve_description }}</p>
                <p><b>链接</b>：{{ selectedCve.cve_url }}</p>
              </div>
           </div>
        </div>
        <div class="graph_container" 
        v-loading="loading"
        element-loading-text="玩命加载中！！！">
          <div id="graph" class="graph"></div>
          
        </div>
      </div>
    </div>

  </template>
  
  <script>
  import { SupplyChain,Get_version,Get_extra } from '@/utils/api/SupplyChain'
  import * as d3 from "d3";
  
  export default {
    name: 'SupplyChain',
    
    data() {
      return {
        loading:false,
        // cve相关数据
        show_cve_list:[],
        selectedCveNo:'',
        selectedCve:{},





        pack_name: '',
        versions:[],
        version:'',
        extras:[''],
        extra:'',
        graph: {
          links: [],
          nodes: [

          ],
        },
      }
    },
    created() {
  
    },
    methods: {
      supply() {
        d3.select("#graph svg").remove();
        let vm = this
        let extra=vm.extra=='无extra'?'':vm.extra
        let data = { 
            'name': vm.pack_name,
            'version':vm.version,
            'extra':extra
     }
        vm.graph.nodes = []
        vm.graph.links = []
        vm.loading=true
        SupplyChain(data).then(function (resp) {
          console.log(resp.data)
          // 添加数据
          resp.data.graph.forEach(item => {
            let tem = {}
            // tem['label'] = 'Article'
            tem['is_root'] = item.is_root
            tem['id'] = item.name
            tem['cves']=item.cves
            tem['has_cve']=item.has_cve

            vm.graph.nodes.push(tem)
  
            item.dependences.forEach(dep => {
              let atem = {}
              atem['source'] = item.name
              atem['target'] = dep
              atem['type'] = 'CITED_BY'
              vm.graph.links.push(atem)
            })
          })
          console.log(vm.graph.nodes)
          console.log(vm.graph.links)
          vm.loading=false
  
          // 绘图
          let box = document.querySelector('.graph_container');
          const width = box.style.width;
           const height = box.style.height; // 修改高度为800
  
          const color = d3.scaleOrdinal(d3.schemeCategory10);

          const types = ["CITED_BY"];
          const strokeWidth = 1.5;
  
          const simulation = d3.forceSimulation(vm.graph.nodes)
            .force("charge", d3.forceManyBody().strength(-3000))
            .force("x", d3.forceX(width / 2+600).strength(0.05))
            .force("y", d3.forceY(height / 2+200).strength(0.05))
            .force(
              "link",
              d3.forceLink(vm.graph.links)
                .id(function (d) {
                  return d.id;
                })
                .distance(100)
                .strength(1)
            )
            .on("tick", ticked);
  
          const svg = d3
            .select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("pointer-events", "all");
  // 箭头
          svg.append("defs")
            .selectAll("marker")
            .data(types)
            .join("marker")
            .attr("id", (d) => `arrow-${d}`)
            .attr("viewBox", "0 0 10 10")
            .attr("refX", 10)
            .attr("refY", 5)
            .attr("markerUnits", strokeWidth)
            .attr("markerWidth", 10)
            .attr("markerHeight", 10)
            .attr("orient", "auto")
            .append("path")
            .attr("fill", color)
            .attr("d", 'M 0 0 L 10 5 L 0 10 z');
  
          const link = svg
            .append("g")
            .selectAll("g")
            .data(vm.graph.links)
            .enter()
            .append("line")
            .attr("stroke", (d) => color(d.type))
            .attr("stroke-width", strokeWidth)
            .attr("marker-end", (d) => `url(${new URL(`#arrow-${d.type}`, location)})`);
  
          const node = svg.append("g")
            .selectAll("g")
            .data(vm.graph.nodes)
            .enter().append("g");
  
          node.append("circle")
            .attr("r", 10) // 修改节点大小为10
            .attr("fill", function (d) {
              // return color(d.is_root);
              return getNodeColor(d);
            });
            // .on("click", this.handleNodeClick);
  
          node.call(
            d3.drag()
              .on("start", dragstarted)
              .on("drag", dragged)
              .on("end", dragended)
          );
  
          node.append("text")
            .text(function (d) {
              return d.id;
            })
            .attr('x', 12) // 调整文本与节点的相对位置
            .attr('y', 4) // 调整文本与节点的相对位置
            .style('fill', 'black');
  
          node.append("title")
            .text(function (d) {
              return d.id;
            });
          node.on("click", vm.handleNodeClick);
          function ticked() {
            node.call(updateNode);
            link.call(updateLink);
          }
  
          function fixna(x) {
            if (isFinite(x)) return x;
            return 0;
          }
  
          function updateLink(link) {
            link.attr("x1", function (d) {
              return fixna(d.source.x);
            })
              .attr("y1", function (d) {
                return fixna(d.source.y);
              })
              .attr("x2", function (d) {
                return fixna(d.target.x);
              })
              .attr("y2", function (d) {
                return fixna(d.target.y);
              });
          }
  
          function updateNode(node) {
            node.attr("transform", function (d) {
              return "translate(" + fixna(d.x) + "," + fixna(d.y) + ")";
            });
          }
  
          function dragstarted(event, d) {
            event.sourceEvent.stopPropagation();
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          }
  
          function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
          }
          const orangeColor = "#FFA500";
          const redColor = "#FF0000";
          const greenColor = "#00FF00";

          // 根据节点的is_root和has_cve属性设置节点的颜色
          function getNodeColor(node) {
            if (node.is_root == 1) {
              // console.log("你好，我现在要开始选颜色了")
              // return orangeColor;
              return "#FFA500"
            } else if (node.has_cve == 1) {
              // return redColor;
              return "#FF0000"
            } else {
              // return greenColor;
              return  "#00FF00"
            }
          }
          function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          }
        })
      },
      search_version(){
        let vm=this
        vm.versions=[]
        vm.version=''
        vm.extra=''
        vm.extras=['']
        let data = { 
            'name': vm.pack_name,
        }
        Get_version(data).then(function(resp){
            console.log(resp.data)
            if(resp.data.status==200)
            {
              vm.$message.success("已找到软件包，请选择版本")
              // console.log("你好，我现在成功了")
              vm.versions=resp.data.versions
            }   
            else
            {
              vm.$message.error("该软件包不存在或已废弃")
            }
        })
      },
      get_extra(){
        let vm=this
        vm.extra=''
        vm.extras=['']
        let data={
            'name':vm.pack_name,
            'version':vm.version
        }
        Get_extra(data).then(function(resp){
            console.log(resp.data)
            if(resp.data.status==200)
            {
              vm.$message.success("请选择extra依赖（可以不选择）")
              vm.extras=resp.data.extra
              vm.extras.push('无extra')
              console.log(vm.extras)
            }   
            else
            {
              vm.$message.error("该软件包不存在或已废弃")
            }

            
            
        })
      },
      handleNodeClick(node) {
    let vm=this
    // vm.$message.success("成功点击")
    let data=node.srcElement.__data__
    console.log(data.cves)
    vm.show_cve_list=data.cves
    // 添加其他节点点击事件的处理逻辑
  },
  handleSelectChange() {
        let selectedCve = this.show_cve_list.find(item => item.cve_no === this.selectedCveNo);
        if (selectedCve) {
          this.selectedCve = selectedCve;
        } else {
          this.selectedCve = {};
        }
      }
    },
  }
  </script>
  
  <style>
  .container{
    display: flex;
    width: 100vw;
    height: 100vh;
    background-color: #e9f3eb;
    flex-direction: column;
    justify-content: space-around;
    align-items: center;
  }
  .input_container{
    display: flex;
    width: 80vw;
    height: 8vh;
    background-color: #f3faf8;
    margin: 10px;
    flex-direction: row;
    justify-content: space-around;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影效果 */
    border-radius: 4px; /* 添加圆角边框 */
  }
  .output_container{
    display: flex;
    width: 95vw;
    height: 80vh;
    background-color: #e9f3eb;
    flex-direction: row;
    justify-content: space-between;
    margin: 10px;
  }
  .static_container{
    display: flex;
    height: 100%;
    width: 17%;
    background-color: #e9f3eb;
    flex-direction: column;
    justify-content: space-between;
    /* box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影效果 */
    /* border-radius: 4px; 添加圆角边框 */ 
  }
  .common_static{
    width: 100%;
    height: 48%;
    background-color: #f3faf8;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影效果 */
    border-radius: 4px; /* 添加圆角边框  */
  }
  .cve_static{
    width: 100%;
    height: 48%;
    background-color: #f3faf8;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影效果 */
    border-radius: 4px; /* 添加圆角边框  */
  }

  .graph_container{
    height: 100%;
    width: 80%;
    background-color: #f3faf8;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); /* 添加阴影效果 */
    border-radius: 4px; /* 添加圆角边框 */
  }
  .graph{
    height: 100%;
    width: 100%;
  }
  </style>
  