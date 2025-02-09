import 'package:flutter/material.dart';
// import 'dart:developer' as dev;
import 'utils.dart';

class MergeGame extends StatefulWidget {
  const MergeGame({super.key});

  @override
  _MergeGameState createState() => _MergeGameState();
}

class _MergeGameState extends State<MergeGame> {
  // 横8マス、縦10マス
  static const int totalColumn = 8;
  static const int totalRow = 8;
  late List<String> items =
      List.generate(totalColumn * totalRow, (index) => "");
  int count = 0;

  @override
  void initState() {
    super.initState();

    // ゲームの更新処理
    Future.doWhile(() async {
      // 毎フレームごとに数字が増える
      if (mounted) {
        setState(() {
          _createNewNumber();
        });
      }
      await Future.delayed(Duration(milliseconds: 20));
      return true;
    });
  }

  void _createNewNumber() {
    if (mounted) {
      setState(() {
        int target = _getTarget(items);
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

  int _getTarget(list) {
    int target = randomIntInRange(0, list.length - 1);
    if (list[target] == "" || list[target] == '1') {
      return target;
    }
    return _getTarget(list);
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
          title: Text('Idle Game'),
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
                        return Container(
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.black), // 枠線
                            borderRadius: BorderRadius.circular(4), // 角丸
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            items[index],
                            style: TextStyle(
                                fontSize: 20, fontWeight: FontWeight.bold),
                          ),
                        );
                      },
                    ),
                  ),
                ),
                SizedBox(height: 20),
                Text(
                  '試行回数: ${count.toString()} ${(count > 200) ? "!!" : ""}',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
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
