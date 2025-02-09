import 'package:flutter/material.dart';
// import 'dart:developer' as dev;
import 'utils.dart';

class IdleGame extends StatefulWidget {
  const IdleGame({super.key});

  @override
  _IdleGameState createState() => _IdleGameState();
}

class _IdleGameState extends State<IdleGame> {
  List<String> moneyIcons = ['💰️', '💲', '💴', '💵', '💶', '💷'];
  String money = '';

  @override
  void initState() {
    super.initState();

    // ゲームの更新処理
    Future.doWhile(() async {
      // 毎フレームごとにお金がたまる
      if (mounted) {
        setState(() {
          money += randomChoice(moneyIcons);
        });
      }
      await Future.delayed(Duration(milliseconds: 160)); // 6fpsに近い更新
      return true;
    });
  }

  void _speedUpCounter() {
    if (mounted) {
      setState(() {
        money += randomChoice(moneyIcons);
      });
    }
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
        body: Align(
          alignment: Alignment.topLeft, // 左上に配置
          child: Padding(
            padding: const EdgeInsets.all(10.0), // 少し余白をつける
            child: Text(
              money,
              style: TextStyle(fontSize: 24),
            ),
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _speedUpCounter,
          tooltip: 'SpeedUp!!',
          child: const Icon(Icons.add),
        ), // This trailing comma makes auto-formatting nicer for build methods.
      ),
    );
  }
}
