import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'simple_game.dart';
import 'idle_game.dart';
import 'merge_game.dart';
import 'drag_game.dart';
import 'merge_game2.dart';
import 'location_game.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: TopPage(), // トップページを最初に表示
      routes: {
        // ルートを登録
        '/simple_game': (context) => SimpleGame(),
        '/idle_game': (context) => IdleGame(),
        '/merge_game': (context) => MergeGame(),
        '/drag_game': (context) => DragGame(),
        '/merge_game2': (context) => MergeGame2(),
        '/location_game': (context) => LocationGame(),
      },
      locale: Locale('ja', 'JP'), // 日本語に設定
      supportedLocales: [
        Locale('en', 'US'),
      ],
      localizationsDelegates: [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ],
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
        child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/simple_game');
                },
                child: Text('ボールゲームを始める'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/idle_game');
                },
                child: Text('放置ゲームを始める'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/merge_game');
                },
                child: Text('自動マージゲームを始める'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/drag_game');
                },
                child: Text('ドラッグゲームを始める'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/merge_game2');
                },
                child: Text('手動マージゲームを始める'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, '/location_game');
                },
                child: Text('位置情報ゲームを始める'),
              )
            ]),
      ),
    );
  }
}
