"""Stable class identities shared by training and prediction storage."""
import hashlib
import json


def model_key(target):
    # Preserve existing Exposure checkpoints and their correction patches.
    return hashlib.sha256(json.dumps(list(target)).encode()).hexdigest()


def configured_targets(project):
    targets = set()
    for name, control in project.parsed_label_config.items():
        if control.get('type') != 'BrushLabels':
            continue
        for to_name in control.get('to_name', []):
            for label in control.get('labels', []):
                targets.add((name, to_name, label))
    return targets


def validate_target(project, target):
    if tuple(target) not in configured_targets(project):
        raise ValueError('프로젝트에 등록된 이미지 브러시 클래스를 선택하세요.')


def prediction_version(target):
    return f'Reference Segmenter · {target[2]} · {model_key(target)[:12]}'


def result_target(region):
    if not isinstance(region, dict) or not isinstance(region.get('value'), dict):
        return None
    labels = region['value'].get('brushlabels', [])
    if region.get('type') != 'brushlabels' or not isinstance(labels, list) or len(labels) != 1:
        return None
    target = (region.get('from_name'), region.get('to_name'), labels[0])
    return target if all(isinstance(value, str) and value for value in target) else None
