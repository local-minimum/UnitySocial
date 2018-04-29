using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

public enum ScoresSort { Ascending, Descending };
public struct ScoreEntry
{
    public int rank;
    public string name;
    public string score;

    public int ScoreAsInt
    {
        get
        {
            return int.Parse(score);
        }
    }

    public float ScoreAsFloat
    {
        get
        {
            return float.Parse(score);
        }
    }

    public ScoreEntry(int rank, string name, string score)
    {
        this.rank = rank;
        this.name = name;
        this.score = score;
    }
}

/// <summary>
/// Transactions with the backed-service for getting and posting
/// highscores.
/// 
/// Note that it requires that you have a static class named
/// Stuff and it have a field Stuff.Txt which contains your
/// secret hash salt. If you wish to hardcode it to this class,
/// then just replace Stuff.Txt with your secret string.
/// </summary>
public class HighScoresGateway : MonoBehaviour {

    [SerializeField]
    int nScores = 10;

    [SerializeField]
    string host = "";

    [SerializeField]
    string service = "";

    [SerializeField]
    string game = "";

    [SerializeField]
    string notTakenName = "[EMPTY]";

    string scoresURI = "//{0}/{1}/highscore/{2}/{3}";
    string scoresNoServiceURI = "//{0}/highscore/{1}/{2}";

    string allowedCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.?!_- 1234567890";

    #region Transactions

    string ScoresURI(string scoreType)
    {
        if (string.IsNullOrEmpty(service))
        {
            return string.Format(scoresNoServiceURI, host, game, scoreType);
        }
        return string.Format(scoresURI, host, service, game, scoreType);
    }

    string ScoresURI(string scoreType, int count)
    {
        return ScoresURI(scoreType) + string.Format("?count={0}", count);
    }

    public void GetHighscores(string scoreType, System.Action<List<ScoreEntry>> callback, System.Action<string> errorCallback)
    {
        string uri = ScoresURI(scoreType, nScores);
        UnityWebRequest request = UnityWebRequest.Get(uri);
        StartCoroutine(Communicator(request, callback, errorCallback));
    }

    public void PostResult(string scoreType, string name, string score, System.Action<List<ScoreEntry>> callback, System.Action<string> errorCallback)
    {
        string uri = ScoresURI(scoreType, nScores);
        string checkSum = GetChecksum(name, score);
        Dictionary<string, string> data = new Dictionary<string, string>();
        data.Add("name", name);
        data.Add("score", score);
        data.Add("checkSum", checkSum);
        UnityWebRequest request = UnityWebRequest.Post(uri, data);
        StartCoroutine(Communicator(request, callback, errorCallback));
    }

    string GetChecksum(string name, string score)
    {
        string msg = name + score + Stuff.Txt;
        System.Security.Cryptography.MD5 md5 = System.Security.Cryptography.MD5.Create();
        byte[] hash = md5.ComputeHash(System.Text.Encoding.UTF8.GetBytes(msg));
        string checkSum = System.BitConverter.ToString(hash).Replace("-", string.Empty);
        return checkSum;
    }

    IEnumerator<WaitForSeconds> Communicator(UnityWebRequest request, System.Action<List<ScoreEntry>> callback, System.Action<string> errorCallback)
    {
        request.SendWebRequest();
        while (!request.isDone)
        {
            yield return new WaitForSeconds(0.25f);
        }
        if (request.isNetworkError)
        {
            errorCallback("Could not connect to highscores server");
        }
        else if (request.isHttpError)
        {
            errorCallback("Highscores server not happy with what you are doing");
        }
        else
        {
            List<ScoreEntry> response = ParseList(request.downloadHandler.text);
            callback(response);
        }
    }

    #endregion

    /// <summary>
    /// Ensures you always get the same number of scores, with predefined
    /// empty-placeholders
    /// </summary>
    /// <param name="scores">The fetched scores</param>
    /// <returns>The padded same scores</returns>
    public List<ScoreEntry> PadScoreList(List<ScoreEntry> scores)
    {
        for (int i = scores.Count; i < nScores; i++)
        {
            scores.Add(new ScoreEntry(
                i + 1,
                notTakenName,
                ""
            ));
        }

        return scores;
    }

    /// <summary>
    /// Helper to limit length and charactrs used in name.
    /// Really only to ensure they will display correctly
    /// </summary>
    /// <param name="name"></param>
    /// <param name="maxLenght"></param>
    /// <returns>The name as it would be accepted</returns>
    public string SecureName(string name, int maxLenght)
    {
        string clean = "";
        for (int i = 0; i<name.Length; i++)
        {
            if (allowedCharacters.IndexOf(name[i]) >= 0) {
                clean += name[i];
            }
        }
        return clean.Substring(0, Mathf.Min(clean.Length, maxLenght));
    }

    private ScoreEntry ParseEntry(string line)
    {
        string[] row = line.Split('\t');
        if (row.Length == 3)
        {
            return new ScoreEntry(
                int.Parse(row[0]),
                row[1],
                row[2]
            );
        }
        return new ScoreEntry();
    }

    private List<ScoreEntry> ParseList(string s)
    {
        List<ScoreEntry> results = new List<ScoreEntry>();
        foreach(string line in s.Split('\n'))
        {
            ScoreEntry e = ParseEntry(line);
            if (e.rank != 0)
            {
                results.Add(e);
            }
        }
        return results;
    }
}
