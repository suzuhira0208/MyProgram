var title = []; //表のタイトル格納用配列
var data = [];  //表データ格納用配列

//色の指定
red_back = 'RGBA(255, 0, 0, 0.2)'; //1年
green_back = 'RGBA(0, 255, 0, 0.2)';//2年
blue_back = 'RGBA(0, 0, 255, 0.2)';//3年
red_border = 'RGBA(255, 0, 0, 1)'; //1年
green_border = 'RGBA(0, 255, 0, 1)';//2年
blue_border = 'RGBA(0, 0, 255, 1)';//3年

//平均(黒)
means_back = 'RGBA(0, 0, 0, 0.2)';
means_border = 'RGBA(0, 0, 0, 1)';
//最小(シアンブルー)
min_back = 'RGBA(102, 255, 255, 0.2)';
min_border = 'RGBA(102, 255, 255, 1)';
//最大(オレンジ)
max_back = 'RGBA(255, 165, 0, 0.2)';
max_border = 'RGBA(255, 165, 0, 1)';
//初期化用
null_color = 'RGBA(255, 255, 255, 0)'

//3学年分表示する用のフラグ
grade_1 = false;
grade_2 = false;
grade_3 = false;


//表からデータを取得して格納するクラス
class Datavalue{
  constructor(data, i){
    this.number = data[i][0];
    this.name = data[i][1];
    this.grade = data[i][2];
    this.japanese = data[i][3];
    this.math = data[i][4];
    this.english = data[i][5];
    this.science = data[i][6];
    this.society = data[i][7];

  }
};


//評価ら取得したデータをレーダーチャートのデータセットに格納するクラス
class Datasets{
  constructor(Datavalue){
    this.label = [Datavalue.number + "番", " " + Datavalue.name + "(" + Datavalue.grade + "年" + ")" ];
    this.data =  [Datavalue.japanese, Datavalue.math, Datavalue.english, Datavalue.science, Datavalue.society];
    if(Datavalue.grade == 1){
      this.backgroundColor = red_back;
      this.borderColor = red_border;
    }else if(Datavalue.grade == 2){
      this.backgroundColor = green_back;
      this.borderColor = green_border;
    }else if(Datavalue.grade == 3){
      this.backgroundColor = blue_back;
      this.borderColor = blue_border;
    }
    this.borderWidth = 1;

  }
};

//CSVデータをスプリットして配列に格納する関数
function csv2Array(str) { //
  var csvData = [];
  var lines = str.split('\n');
  title = lines[0].split(',');
  for (var i = 1; i < lines.length; ++i) {
    var cells = lines[i].split(',');
    data.push(cells);
  };
};

//CSVデータが格納された配列から表を生成して描画する関数
function drawtable(data){
  var table = document.getElementById('table');
  var duplicate_number = [];
  var duplicate_cnt = 1;
  var prev_number; //一つ前の番号を記憶する用の変数
  var index_cnt = 0;

  data = data.slice(0, -1);


  let insertElement = ''; //テーブルタグを表示するようの変数

  insertElement += '<thead>'
  insertElement += '<tr>'
  title.forEach((element) => {
    insertElement += `<th>${element}</th>`

  });
  insertElement += '</tr>'
  insertElement += '</thead>'

  insertElement += '<tbody class = "list">'
  data.forEach((element) => { //配列の中身を表示
    insertElement += '<tr>'; //改行

    element.forEach((childElement) =>{ //element配列の要素

      insertElement += `<td>${childElement}</td>`
    });

    insertElement += `<td><input type = "checkbox" name = "options" value = ${String(index_cnt)}></td>` //チェックボックス
    insertElement += '</tr>'; //改行
    index_cnt ++;

  });
  insertElement += '</tbody>'
  table.innerHTML = insertElement; // 表示

  $(document).ready(function()
  {
    $("#table").tablesorter();
  });
};

//レーダーチャートを描画する関数(初期状態)
function drawradar(){
  var ctx = document.getElementById('radar');
  ctx.style.position = "absolute";
  ctx.style.left = "500px";
  ctx.style.top = "-570px";
  var ctx = ctx.getContext("2d")

  radar_model = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [title[3], title[4], title[5], title[6], title[7]],

      //データセット
      datasets : [{
        label: "",
        data: [0, 0, 0, 0, 0],
        backgroundColor: null_color,
        borderColor: null_color,
        borderWidth: 1,

      },{
        label: "",
        data: [0, 0, 0, 0, 0],
        backgroundColor: null_color,
        borderColor: null_color,
        borderWidth: 1,

      },{
        label: "",
        data: [0, 0, 0, 0, 0],
        backgroundColor: null_color,
        borderColor: null_color,
        borderWidth: 1,

      }]
    },
    options: {
        title: {
          display : true,
          text : '試験成績'
        },
        scale: {
          ticks:{
            //最小値の値を0に指定
            beginAtZero:true,
            min : 0,
            //最大値を指定
            max : 100,
          }
        },
        maintainAspectRatio : false
      }
  });
};


//レーダーチャートを更新する度に初期化する関数
function initialize_datasets(){
  delete_grade();
  table_details = document.getElementById('details');
  while(table_details.rows[0]) table_details.deleteRow(0);

  for(i = 0; i < 3; i++){
    radar_model.data.datasets[i].label = "";
    radar_model.data.datasets[i].data = [0, 0, 0, 0, 0];
    radar_model.data.datasets[i].backgroundColor = null_color;
    radar_model.data.datasets[i].borderColor = null_color;
    radar_model.data.datasets[i].borderwidth = 1;
  }
  japanese_temp = 0;
  math_temp = 0;
  english_temp = 0;
  science_temp = 0;
  society_temp = 0;
  cnt_temp = 0;

};

//学年フラグを初期化する関数
function delete_grade(){
  grade_1 = false
  grade_2 = false
  grade_3 = false
};

//表示ボタンが押されたときに実行される関数
function display_botton(){
  //delete_grade();
  initialize_datasets();
  var elements = document.querySelectorAll("input[name = options]");
  for(i = 0; i < elements.length; i++){
    if(elements[i].checked){
      dataupdate(elements[i].value);
    }
  }
  radar_model.update();
};

//レーダーチャート内のデータを更新する関数
function dataupdate(i){
  var input_value = new Datavalue(data, i);
  var input_datasets = new Datasets(input_value);


  if(grade_1 == false){
    radar_model.data.datasets[0].label = input_datasets.label;
    radar_model.data.datasets[0].data = input_datasets.data;
    radar_model.data.datasets[0].backgroundColor = input_datasets.backgroundColor;
    radar_model.data.datasets[0].borderColor = input_datasets.borderColor;
    grade_1 = true

  }else if(grade_2 == false){
    radar_model.data.datasets[1].label = input_datasets.label;
    radar_model.data.datasets[1].data = input_datasets.data;
    radar_model.data.datasets[1].backgroundColor = input_datasets.backgroundColor;
    radar_model.data.datasets[1].borderColor = input_datasets.borderColor;
    grade_2 = true

  }else if(grade_3 == false){
    radar_model.data.datasets[2].label = input_datasets.label;
    radar_model.data.datasets[2].data = input_datasets.data;
    radar_model.data.datasets[2].backgroundColor = input_datasets.backgroundColor;
    radar_model.data.datasets[2].borderColor = input_datasets.borderColor;
    grade_3 = true

  }
};

//平均ボタンが押されたときに実行される関数
function means_botton(){
  //delete_grade();
  initialize_datasets();
  var elements = document.querySelectorAll("input[name = options]");
  for(i = 0; i < elements.length; i++){
    if(elements[i].checked){
      calcu_means(elements[i].value);
    }
  }
  japanese_temp = japanese_temp / cnt_temp;
  math_temp = math_temp / cnt_temp;
  english_temp = english_temp / cnt_temp;
  science_temp = science_temp / cnt_temp;
  society_temp = society_temp / cnt_temp;
  radar_model.data.datasets[0].label = "平均"
  radar_model.data.datasets[0].data = [japanese_temp, math_temp, english_temp, science_temp, society_temp];
  radar_model.data.datasets[0].backgroundColor = means_back;
  radar_model.data.datasets[0].borderColor = means_border;
  radar_model.update();
  draw_details();
};

//平均値を取得する関数
function calcu_means(i){

  var temp_value = new Datavalue(data, i);
  japanese_temp += Number(temp_value.japanese);
  math_temp += Number(temp_value.math);
  english_temp += Number(temp_value.english);
  science_temp += Number(temp_value.science);
  society_temp += Number(temp_value.society);
  cnt_temp ++;

};

//最小ボタンが押されたときに実行される関数
function min_botton(){
  initialize_datasets();
  var elements = document.querySelectorAll("input[name = options]");
  for(i = 0; i < elements.length; i++){
    if(elements[i].checked){
      calcu_min(elements[i].value);
    }
  }
  radar_model.data.datasets[0].label = "最小"
  radar_model.data.datasets[0].data = [japanese_temp, math_temp, english_temp, science_temp, society_temp];
  radar_model.data.datasets[0].backgroundColor = min_back;
  radar_model.data.datasets[0].borderColor = min_border;
  radar_model.update();
  draw_details();
};

//最小値を取得する関数
function calcu_min(i){
  var temp_value = new Datavalue(data, i);
  if(cnt_temp == 0){
    japanese_temp = Number(temp_value.japanese);
    math_temp = Number(temp_value.math);
    english_temp = Number(temp_value.english);
    science_temp = Number(temp_value.science);
    society_temp = Number(temp_value.society);

  }else{
    if(japanese_temp > Number(temp_value.japanese)){
      japanese_temp = Number(temp_value.japanese);
    }
    if(math_temp > Number(temp_value.math)){
      math_temp = Number(temp_value.math);
    }
    if(english_temp > Number(temp_value.english)){
      english_temp = Number(temp_value.english);
    }
    if(science_temp > Number(temp_value.science)){
      science_temp = Number(temp_value.science);
    }
    if(society_temp > Number(temp_value.society)){
      society_temp = Number(temp_value.society);
    }
  }
  cnt_temp ++;
};

//最大ボタンが押されたときに実行される関数
function max_botton(){
  initialize_datasets();
  var elements = document.querySelectorAll("input[name = options]");
  for(i = 0; i < elements.length; i++){
    if(elements[i].checked){
      calcu_max(elements[i].value);
    }
  }
  radar_model.data.datasets[0].label = "最大"
  radar_model.data.datasets[0].data = [japanese_temp, math_temp, english_temp, science_temp, society_temp];
  radar_model.data.datasets[0].backgroundColor = max_back;
  radar_model.data.datasets[0].borderColor = max_border;
  radar_model.update();
  draw_details();

};

//最大値を取得する関数
function calcu_max(i){
  var temp_value = new Datavalue(data, i);
  if(japanese_temp < Number(temp_value.japanese)){
    japanese_temp = Number(temp_value.japanese);
  }
  if(math_temp < Number(temp_value.math)){
    math_temp = Number(temp_value.math);
  }
  if(english_temp < Number(temp_value.english)){
    english_temp = Number(temp_value.english);
  }
  if(science_temp < Number(temp_value.science)){
    science_temp = Number(temp_value.science);
  }
  if(society_temp < Number(temp_value.society)){
    society_temp = Number(temp_value.society);
  }
  cnt_temp ++;
};





//科目ごとの平均、最小、最大それぞれの数値を表にして描画する関数
function draw_details(){
  table_details = document.getElementById('details');
  let insert_details_data = '';
  insert_details_data += '<tr>';
  insert_details_data += `<th>${radar_model.data.datasets[0].label}</th>`
  insert_details_data += '</tr>';

  insert_details_data += '<tr>'
  insert_details_data += `<td>${"国語"}</td>`
  insert_details_data += `<td>${String(radar_model.data.datasets[0].data[0])}</td>`
  insert_details_data += '</tr>'

  insert_details_data += '<tr>'
  insert_details_data += `<td>${"数学"}</td>`
  insert_details_data += `<td>${String(radar_model.data.datasets[0].data[1])}</td>`
  insert_details_data += '</tr>'

  insert_details_data += '<tr>'
  insert_details_data += `<td>${"英語"}</td>`
  insert_details_data += `<td>${String(radar_model.data.datasets[0].data[2])}</td>`
  insert_details_data += '</tr>'

  insert_details_data += '<tr>'
  insert_details_data += `<td>${"理科"}</td>`
  insert_details_data += `<td>${String(radar_model.data.datasets[0].data[3])}</td>`
  insert_details_data += '</tr>'

  insert_details_data += '<tr>'
  insert_details_data += `<td>${"社会"}</td>`
  insert_details_data += `<td>${String(radar_model.data.datasets[0].data[4])}</td>`
  insert_details_data += '</tr>'

  table_details.innerHTML = insert_details_data;

};


function main() {
    var req = new XMLHttpRequest();
    var filePath = 'http://www.mn.cis.iwate-u.ac.jp/~nakaya/report/Data.csv'; //CSVファイルのパスは適宜変更してください。
    req.open('GET', filePath, true);
    req.send(null);
    req.onload = function() {
        csv2Array(req.responseText);
        drawtable(data);
        drawradar();
      }
};

//メイン(初期状態)
main();
