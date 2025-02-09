import 'package:flutter/material.dart';
// import 'dart:developer' as dev;
import 'utils.dart';

class MergeGame2 extends StatefulWidget {
  const MergeGame2({super.key});

  @override
  _MergeGame2State createState() => _MergeGame2State();
}

class _MergeGame2State extends State<MergeGame2> {
  // 横8マス、縦10マス
  static const int totalColumn = 8;
  static const int totalRow = 8;
  late List<String> items =
      List.generate(totalColumn * totalRow, (index) => "");
  int count = 0;
  int durationMilliseconds = 1000;
  bool isOver = false;
  late Text messageText;

  @override
  void initState() {
    super.initState();

    // ゲームの更新処理
    Future.doWhile(() async {
      if (isOver) {
        return false;
      }
      // 毎フレームごとに数字が増える
      if (mounted) {
        setState(() {
          _createNewNumber();
        });
      }
      if (durationMilliseconds > 30) {
        durationMilliseconds--;
      }
      await Future.delayed(Duration(milliseconds: durationMilliseconds));
      return true;
    });
  }

  void _createNewNumber() {
    if (mounted) {
      setState(() {
        int? target = _getTarget(items);
        if (target == null) {
          return;
        }
        late int value;
        if (items[target] == '') {
          value = 1;
        } else if (items[target] == '1') {
          value = 2;
        }
        items[target] = value.toString();
        autoMerge(items, target, value);
        count++;
      });
    }
  }

  int? _getTarget(list, {int retry = 0}) {
    int target = randomIntInRange(0, list.length - 1);
    if (list[target] == "" || list[target] == '1') {
      return target;
    }
    retry++;
    if (retry % 50 == 0) {
      bool isEnd = true;
      for (var item in list) {
        if (item == '' || item == '1') {
          isEnd = false;
          break;
        }
      }
      if (isEnd) {
        isOver = true;
        return null;
      }
    }
    return _getTarget(list, retry: retry);
  }

  void autoMerge(list, target, value) {
    List<int> surroundingValues = getSurroundingValues(target);
    for (var val in surroundingValues) {
      if (list[val] == value.toString()) {
        list[target] = (value * 2).toString();
        list[val] = '';
        autoMerge(list, target, value * 2);
        break;
      }
    }
  }

  List<int> getSurroundingValues(int num) {
    List<int> surroundingValues = [];
    // 最上段でない場合
    if (num >= totalColumn) {
      surroundingValues.add(num - totalColumn);
    }
    // 左端でない場合
    if (num % totalColumn != 0) {
      surroundingValues.add(num - 1);
    }
    // 右端でない場合
    if (num % totalColumn != totalColumn - 1) {
      surroundingValues.add(num + 1);
    }
    // 最下段でない場合
    if (num < totalColumn * totalRow - totalColumn) {
      surroundingValues.add(num + totalColumn);
    }

    return surroundingValues;
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: Text('Auto Merge Game'),
          leading: IconButton(
            icon: Icon(Icons.arrow_back), // 戻るアイコン
            onPressed: () {
              Navigator.pop(context); // トップページに戻る
            },
          ),
        ),
        body: Center(
          child: Column(
              mainAxisAlignment: MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                SizedBox(
                  height: 420, // 高さを固定
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: GridView.builder(
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 8, // 4列のグリッド
                        childAspectRatio: 5 / 4, // 横セル:縦セルの比率
                        crossAxisSpacing: 0, // 水平方向の間隔
                        mainAxisSpacing: 0, // 垂直方向の間隔
                      ),
                      itemCount: items.length,
                      itemBuilder: (context, index) {
                        if (isOver || items[index] == "") {
                          return Container(
                            width: 50,
                            height: 50,
                            decoration: BoxDecoration(
                              border: Border.all(color: Colors.black), // 枠線
                              borderRadius: BorderRadius.circular(4), // 角丸
                            ),
                            child: Center(
                              child: Text(
                                items[index],
                                style: TextStyle(
                                    fontSize: 20, fontWeight: FontWeight.bold),
                              ),
                            ),
                          );
                        } else {
                          return DragTarget<int>(
                            onAcceptWithDetails: (details) {
                              int fromIdx = details.data;
                              setState(() {
                                if (index != fromIdx &&
                                    items[index] == items[fromIdx]) {
                                  items[index] =
                                      (int.parse(items[index]) * 2).toString();
                                  items[fromIdx] = '';
                                  count++;
                                }
                              });
                            },
                            builder: (context, candidateData, rejectedData) {
                              return Draggable<int>(
                                data: index,
                                feedback: Material(
                                  color: Colors.transparent,
                                  child: Container(
                                    width: 50,
                                    height: 40,
                                    color:
                                        const Color.fromARGB(127, 96, 125, 139),
                                    child: Center(
                                        child: Text(
                                      items[index],
                                      style: TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold),
                                    )),
                                  ),
                                ),
                                childWhenDragging: Container(), // ドラッグ中のデータ（任意）
                                child: Container(
                                  width: 50,
                                  height: 50,
                                  decoration: BoxDecoration(
                                    border:
                                        Border.all(color: Colors.black), // 枠線
                                    borderRadius:
                                        BorderRadius.circular(4), // 角丸
                                  ),
                                  child: Center(
                                    child: Text(
                                      items[index],
                                      style: TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                ),
                              );
                            },
                          );
                        }
                      },
                    ),
                  ),
                ),
                SizedBox(height: 20),
                Text(
                  '${isOver ? "ゲームオーバー!!" : ""} 試行回数: ${count.toString()} ${(count > 200) ? "!!" : ""}',
                  style: TextStyle(
                      color: isOver
                          ? Color.fromARGB(255, 200, 50, 50)
                          : Colors.black,
                      fontSize: 20,
                      fontWeight: FontWeight.bold),
                ),
              ]),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _createNewNumber,
          tooltip: 'CreateNumber!!',
          child: const Icon(Icons.add),
        ), // This trailing comma makes auto-formatting nicer for build methods.
      ),
    );
  }
}
