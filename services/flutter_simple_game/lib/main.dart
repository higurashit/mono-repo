import 'package:flutter/material.dart';
import 'simple_game.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: TopPage(), // トップページを最初に表示
      routes: {
        '/simple_game': (context) => SimpleGame(), // ルートを登録
      },
    );
  }
}

class TopPage extends StatelessWidget {
  const TopPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('トップページ'),
      ),
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            // ボタンが押された時、SimpleGame 画面に遷移
            Navigator.pushNamed(context, '/simple_game');
          },
          child: Text('ゲームを始める'),
        ),
      ),
    );
  }
}
