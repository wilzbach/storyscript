## 1) New _Patch_ release (x.y.Z)

#### 1.1) [Create a new git tag  from `stable`](https://github.com/storyscript/storyscript/releases/new?target=stable)


![image](https://user-images.githubusercontent.com/4370550/62307103-44d47300-b483-11e9-8bcb-2879ed0bae38.png)

**Template:**


```
Bug fixes :bug:
-------------

```

---------

## 2) New _minor_ release (x.Y.z)

#### 2.1) Merge `master` into `stable`

Option A: [via GitHub](https://github.com/storyscript/storyscript/compare/stable...master?expand=1&title=Merge%20upstream/master%20into%20upstream/stable).
(make sure to use a _Merge Commit_)

Option B: via CLI

```sh
git fetch upstream
git branch -D master_stable
git checkout upstream/stable
git branch -b master_stable
git merge upstream/stable
```


#### 2.2) [Create a new git tag from `stable`](https://github.com/storyscript/storyscript/releases/new?target=stable)

![image](https://user-images.githubusercontent.com/4370550/62307594-2de25080-b484-11e9-8846-5b65f0211f21.png)


**Template:**

```
New features :rocket:
------------


Bug fixes :bug:
-------------


Other changes :ocean:
--------------------

```


---------

Merge stable back into `master`
-------------------------

tl;dr: We want bug fixes to move back to `master`.
This is done automatically. Simply merge the update PR bot by the `storyscript-infra` account.

---------

Update dependents
-----------------

tl;dr: All tools using Storyscript need to be updated.
This is done semi-automatically. The respective update PRs will automatically be opened by the `storyscript-infra` account.
Dependents:

- [CLI](https://github.com/storyscript/cli)
- [SLS](https://github.com/storyscript/sls) (+VSCode, +Atom)
- [Runtime](https://github.com/storyscript/runtime)
