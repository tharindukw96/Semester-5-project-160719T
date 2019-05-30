import pytest

from testing_app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app.test_client()


@pytest.mark.homepage
def test_homepage(app):
    response = app.get("/")
    assert response.status_code == 200
    #create the home page test script
    assert b"Republican" in response.data, "HomePageTest Success!"

@pytest.mark.addkeyword
def test_addkeyword(app):
    response = app.get("/add")
    assert response.status_code == 200
    assert b"Add new keyword to analyze" in response.data


@pytest.mark.Postaddkeyword
def test_post_addkeyword(app):
    response = app.post("/add_key",data=dict(key='Gun'))
    assert response.status_code == 200
    assert b"Success!" in response.data


@pytest.mark.Postaddkeyword_Duplicate
def test_post_addkeyword_duplicate(app):
    #addd duplicate keyword test
    response = app.post("/add_key",data=dict(key='Gun'))
    assert response.status_code == 200
    assert b"Failed!" in response.data

@pytest.mark.about
def test_about(app):
    
    response = app.get("/about")
    assert response.status_code == 404

@pytest.mark.result
def test_keyword_result(app):
    #Test keyword result
    response = app.get("/analyze?i=Education&tf=7d")
    assert response.status_code == 200
    assert b"Education" in response.data

@pytest.mark.tweetboard
def test_tweet_board(app):
    response = app.get("/tweets?i=Education&tf=7d")
    #assert response.status_code == 200
    assert b"Education" in response.data

@pytest.mark.tweetboard1
def test_tweet_board1(app):
    response = app.get("/tweets?i=War&tf=7d")
    #assert response.status_code == 200
    assert b"War" in response.data

@pytest.mark.tweetboard2
def test_tweet_board2(app):
    response = app.get("/tweets?i=Economics&tf=7d")
    #Response code 200 check -- assert response.status_code == 200
    assert b"Economics" in response.data

@pytest.mark.tweetboard3
def test_tweet_board3(app):
    response = app.get("/tweets?i=Republican&tf=7d")
    #assert response.status_code == 200
    assert b"Republican" in response.data



@pytest.mark.emotiontimeline
def test_emotiontimeline(app):
    response = app.get("/data?i=Education&tf=7d&emotion=Angry")
    assert response.status_code == 200

@pytest.mark.emotiontimeline1
def test_emotiontimeline1(app):
    response = app.get("/data?i=Education&tf=30d&emotion=Angry")
    assert response.status_code == 200

@pytest.mark.emotiontimeline2
def test_emotiontimeline2(app):
    response = app.get("/data?i=War&tf=7d&emotion=Angry")
    assert response.status_code == 200

@pytest.mark.emotiontimeline3
def test_emotiontimeline3(app):
    response = app.get("/data?i=Republican&tf=7d&emotion=Happy")
    assert response.status_code == 200

@pytest.mark.emotiontimeline4
def test_emotiontimeline4(app):
    response = app.get("/data?i=Republican&tf=7d&emotion=Sad")
    assert response.status_code == 200
    
@pytest.mark.heatmap
def test_heatmap(app):
    
    response = app.get("/heatmap/?i=Education&tf=30d")
    assert response.status_code == 200
    assert b"" in response.data

@pytest.mark.heatmap1
def test_heatmap1(app):
    
    response = app.get("/heatmap/?i=War&tf=30d")
    assert response.status_code == 200
    assert b"" in response.data

@pytest.mark.heatmap2
def test_heatmap2(app):
    
    response = app.get("/heatmap/?i=Republican&tf=30d")
    assert response.status_code == 200
    assert b"" in response.data


@pytest.mark.heatmap3
def test_heatmap3(app):
    
    response = app.get("/heatmap/?i=Republican&tf=7d")
    assert response.status_code == 200
    assert b"" in response.data

@pytest.mark.heatmap4
def test_heatmap4(app):
    
    response = app.get("/heatmap/?i=Immigration&tf=7d")
    assert response.status_code == 200
    assert b"" in response.data


@pytest.mark.homepage1
def test_homepage1(app):
    
    response = app.get("/")
    assert response.status_code == 200
    assert b"Republican" in response.data, "Test Success! - Homepage"

@pytest.mark.heatmap5
def test_heatmap5(app):
    
    response = app.get("/heatmap/?i=Economics&tf=7d")
    assert response.status_code == 200
    assert b"" in response.data
    
@pytest.mark.Postaddkeyword_1Duplicate
def test_post_addkeyword_1duplicate(app):
    
    response = app.post("/add_key",data=dict(key='Gun'))
    assert response.status_code == 200
    assert b"Failed!" in response.data





